import time
import threading
import signal
import sys

from sensors import flow, pir, gas, dht, rfid
from actuators import led, fan, servo
import camera
import mqtt_client
import config

# Thread class for sensors which need to run at different polling intervals
class SensorWorker(threading.Thread):
    def __init__(self, name, interval_sec, function, key):
        super().__init__(daemon=True)
        self.name = name
        self.interval = interval_sec
        self.function = function
        self.key = key
        self._stop = threading.Event()

    def run(self):
        print(f"[THREAD] {self.name} started with interval {self.interval}s")
        while not self._stop.is_set():
            try:
                value = self.function()
                if value is not None:
                    if isinstance(value, tuple):
                        payload = dict(zip(self.key, value))
                    else:
                        payload = {self.key: value}
                    mqtt_client.publish_telemetry(payload)
            except Exception as e:
                print(f"[ERROR] {self.name}: {e}")
            time.sleep(self.interval)

    def stop(self):
        self._stop.set()

# Thread function to handle 2 PIR sensors and capture images on motion detection
def motion_worker():
    print("[THREAD] Motion detection image worker started.")
    while True:
        pir.motion_queue.get()
        img_path = camera.capture_image()
        camera.send_alert_email(img_path)
        mqtt_client.publish_telemetry({
            "event": "image_captured",
            "status": "email_sent"
        })
        pir.motion_queue.task_done()


def exit_gracefully(signum, frame):
    print("\n[EXIT] Cleaning up...")
    dht.cleanup()
    camera.cleanup()
    mqtt_client.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    print("[START] SmartHome system initializing...")

    mqtt_client.start()
    servo.init_servo()
    print("[INIT] MQTT, Fan, Servo initialized.")

    threading.Thread(target=motion_worker, daemon=True).start()
    threading.Thread(target=rfid.rfid_loop, daemon=True).start()
    print("[THREAD] RFID reader started.")

    SensorWorker("FlowWorker", 1.0, flow.get_flow_rate, "flow_rate").start()
    SensorWorker("GasWorker", 2.0, gas.read, "air_quality").start()
    SensorWorker("DHTWorker", 15.0, dht.read, ["temperature", "humidity"]).start()
    print("[THREAD] Sensor workers started.")

    last_fan_trigger = time.time()

    print("[MAIN LOOP] Entering main loop. Press Ctrl+C to exit.")
    while True:
        try:
            motion1 = pir.check_motion_1()
            motion2 = pir.check_motion_2()

            led.set_led1(motion1 or mqtt_client.light_state)
            led.set_led2(motion1 or motion2 or mqtt_client.light_state2)
            led.set_led3(mqtt_client.light_state3)
            led.set_led4(mqtt_client.light_state4)

            mqtt_client.publish_telemetry({
                "motion_1": motion1,
                "motion_2": motion2,
                "led_1": led.is_led1_on(),
                "led_2": led.is_led2_on()
            })

            temp = mqtt_client.latest_temperature
            air_quality = mqtt_client.latest_air_quality

            manual_override = mqtt_client.fan_manual_override
            manual_state = mqtt_client.fan_manual_state
            window_manual_override = mqtt_client.window_manual_override

            auto_trigger = air_quality == 1 or (temp is not None and temp >= config.FAN_TEMP_THRESHOLD)
            if auto_trigger:
                last_fan_trigger = time.time()
                print("[AUTO] Fan/Window trigger activated.")
                if not servo.is_window_open():
                    servo.open_window()

            if flow.get_flow_rate() > 2.5:
                led.set_alert_led(True)
            else:
                led.set_alert_led(False)

            if manual_override:
                if manual_state:
                    fan.on()
                    servo.open_window()
                else:
                    fan.off()
            else:
                if time.time() - last_fan_trigger <= config.FAN_HOLD_TIME:
                    fan.on()
                else:
                    fan.off()
                    if servo.is_window_open() and not window_manual_override:
                        servo.close_window()

            mqtt_client.publish_telemetry({
                "fan_state": fan.is_on(),
                "fan_auto": not manual_override and (time.time() - last_fan_trigger <= config.FAN_HOLD_TIME),
                "fan_manual_override": manual_override,
                "fan_manual_state": manual_state
            })

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[EXIT] Keyboard interrupt received. Cleaning up...")
            exit_gracefully(None, None)
        except Exception as e:
            print(f"[ERROR] Exception in main loop: {e}")
            time.sleep(1)

import time
import threading
import signal
import sys

from sensors import flow, pir, gas, dht, rfid
import actuators.led as led
from actuators.servo import init_servo, open_window
from actuators import fan
import camera as alert
import mqtt_client as mqtt
import actuators.fan as fan
import config

# Thread class for time-based sensor polling
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
                    mqtt.publish_telemetry(payload)
            except Exception as e:
                print(f"[ERROR] {self.name}: {e}")
            time.sleep(self.interval)

    def stop(self):
        self._stop.set()

# PIR motion event worker
def motion_worker():
    print("[THREAD] Motion detection image worker started.")
    while True:
        pir.motion_queue.get()
        img_path = alert.capture_image()
        alert.send_alert_email(img_path)
        mqtt.publish_telemetry({"event": "image_captured", "event": "email_sent"})
        pir.motion_queue.task_done()

# Handle graceful exit
def exit_gracefully(signum, frame):
    print("\n[EXIT] Cleaning up...")
    dht.cleanup()
    alert.cleanup()
    mqtt.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

# Main Program
if __name__ == "__main__":
    print("[START] SmartHome system initializing...")

    mqtt.start()
    init_servo()

    print("[INIT] MQTT, Fan, Servo initialized.")

    threading.Thread(target=motion_worker, daemon=True).start()
    threading.Thread(target=rfid.rfid_loop, daemon=True).start()
    print("[THREAD] RFID reader started.")

    # Sensor polling threads
    SensorWorker(name="FlowWorker", interval_sec=1.0, function=flow.get_flow_rate, key="flow_rate").start()
    SensorWorker(name="GasWorker", interval_sec=2.0, function=gas.read, key="air_quality").start()
    SensorWorker(name="DHTWorker", interval_sec=15.0, function=dht.read, key=["temperature", "humidity"]).start()
    print("[THREAD] Sensor workers started.")

    last_fan_trigger = time.time()


    print("[MAIN LOOP] Entering main loop. Press Ctrl+C to exit.")
    while True:
        try:
            motion1 = pir.check_motion_1()
            motion2 = pir.check_motion_2()

            led.set_led1(motion1 or mqtt.light_state)
            led.set_led2(motion1 or motion2 or mqtt.light_state2)
            led.set_led3(mqtt.light_state3)
            led.set_led4(mqtt.light_state4)

            mqtt.publish_telemetry({
                "motion_1": motion1,
                "motion_2": motion2,
                "led_1": led.is_led1_on(),
                "led_2": led.is_led2_on()
            })

            # Read sensor values
            temp = mqtt.latest_temperature
            air_quality = mqtt.latest_air_quality

            # Check override status
            manual_override = mqtt.fan_manual_override
            manual_state = mqtt.fan_manual_state

            # Check auto trigger condition
            auto_trigger = (air_quality == 1) or (temp is not None and temp >= config.FAN_TEMP_THRESHOLD)
            if auto_trigger:
                last_fan_trigger = time.time()
                print("[AUTO] Fan/Window trigger activated.")

            # Fan logic
            if manual_override:
                if manual_state:
                    fan.on()
                    open_window()
                else:
                    fan.off()
            else:
                if time.time() - last_fan_trigger <= config.FAN_HOLD_TIME:
                    fan.on()
                else:
                    fan.off()

            mqtt.publish_telemetry({
                "fan_state": fan.is_on(),
                "fan_auto": not manual_override and (time.time() - last_fan_trigger <= config.FAN_HOLD_TIME),
                "fan_manual_override": manual_override,
                "fan_manual_state": manual_state
            })

            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] Exception in main loop: {e}")
            exit_gracefully(None, None)



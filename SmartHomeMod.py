import time
import threading
import signal
import sys
from sensors import flow, pir, gas, dht, rfid
import actuators.led as led
from actuators.servo import init_servo
import camera as alert
import mqtt_client as mqtt
import actuators.fan as fan
import config


def motion_worker():
    while True:
        pir.motion_queue.get()
        img = alert.capture_image()
        alert.send_alert_email(img)
        mqtt.publish_telemetry({"event": "image_captured"})
        mqtt.publish_telemetry({"event": "email_sent"})
        pir.motion_queue.task_done()


def exit_gracefully(signum, frame):
    print("\n[EXIT] Cleaning up...")
    dht.cleanup()
    alert.cleanup()
    mqtt.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    print("Starting system...")
    mqtt.start()
    init_servo()
    threading.Thread(target=motion_worker, daemon=True).start()  # PIR motion image handler
    threading.Thread(target=rfid.rfid_loop, daemon=True).start()  # RFID reader loop

    last_dht = last_mq = last_flow = last_fan_trigger = time.time()
    last_temp = last_hum = None
    last_aq = 0


    while True:
        now = time.time()

        # --- Sensor Reads ---
        if now - last_flow >= 1:
            mqtt.publish_telemetry({"flow_rate": flow.get_flow_rate()})
            last_flow = now

        if now - last_dht >= 15:
            t, h = dht.read()
            last_temp = t
            last_hum = h
            mqtt.publish_telemetry({"temperature": t, "humidity": h})
            t, h = last_temp, last_hum
        else:
            t, h = None, None

        if now - last_mq >= 2:
            aq = gas.read()
            last_aq = aq
            mqtt.publish_telemetry({"air_quality": aq})
            last_mq = last_aq
        else:
            aq = 0

        # --- Motion Detection ---
        motion1 = pir.check_motion_1()
        motion2 = pir.check_motion_2()

        # --- LED Logic ---
        led.set_led1(motion1 or mqtt.light_state)
        led.set_led2(motion1 or motion2 or mqtt.light_state2)
        led.set_led3(mqtt.light_state3)
        led.set_led4(mqtt.light_state4)

        mqtt.publish_telemetry({
            "motion_1": motion1,
            "motion_2": motion2,
            "light_1": led.is_led1_on(),
            "light_2": led.is_led2_on()
        })

        # --- Fan Control Logic ---
        auto_fan_on = (aq == 1) or (t is not None and t >= config.FAN_TEMP_THRESHOLD)
        if auto_fan_on:
            last_fan_trigger = now

        manual_fan_override = getattr(mqtt, "fan_manual_override", False)
        manual_fan_state = getattr(mqtt, "fan_manual_state", False)

        if manual_fan_override:
            fan.on() if manual_fan_state else fan.off()
        else:
            fan.on() if now - last_fan_trigger <= config.FAN_HOLD_TIME else fan.off()

        mqtt.publish_telemetry({
            "fan_state": fan.is_on(),
            "fan_auto": not manual_fan_override and (now - last_fan_trigger <= config.FAN_HOLD_TIME),
            "fan_manual_override": manual_fan_override,
            "fan_manual_state": manual_fan_state
        })

        time.sleep(0.5)

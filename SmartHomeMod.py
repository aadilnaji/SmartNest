import time
import threading
import signal
import sys
from sensors import flow, pir, gas, dht, rfid
import actuators.led as led
import camera as alert
import mqtt_client as mqtt



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
    threading.Thread(target=motion_worker, daemon=True).start()  # Start PIR loop
    threading.Thread(target=rfid.rfid_loop, daemon=True).start() # Start RFID reader loop

    last_dht = last_mq = last_flow = time.time()

    while True:
        now = time.time()

        if now - last_flow >= 1:
            mqtt.publish_telemetry({"flow_rate": flow.get_flow_rate()})
            last_flow = now

        if now - last_dht >= 15:
            t, h = dht.read()
            mqtt.publish_telemetry({"temperature": t, "humidity": h})
            last_dht = now

        if now - last_mq >= 2:
            aq = gas.read()
            mqtt.publish_telemetry({"air_quality": aq})
            last_mq = now

        motion1 = pir.check_motion_1()
        motion2 = pir.check_motion_2()

        if mqtt.light_state or motion1:
            led.set_led1(True)
        else:
            led.set_led1(False)
            
        mqtt.publish_telemetry({
        "motion_1": motion1,
        "motion_2": motion2,
        "light_1": led.is_led1_on(),
        "light_2": led.is_led2_on()
        } )

        time.sleep(0.5)

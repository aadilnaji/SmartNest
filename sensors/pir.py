import time
from gpiozero import DigitalInputDevice
from queue import Queue
from config import PIR_PIN, MOTION_TO

pir_sensor = DigitalInputDevice(PIR_PIN)
motion_queue = Queue()
last_motion_time = 0


def check_motion():
    global last_motion_time
    if pir_sensor.value:
        last_motion_time = time.time()
        if motion_queue.empty():
            motion_queue.put(True)
        return True
    return (time.time() - last_motion_time) <= MOTION_TO
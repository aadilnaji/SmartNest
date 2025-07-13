import time
from gpiozero import DigitalInputDevice
from queue import Queue
from config import PIR_PIN, PIR2_PIN, MOTION_TO

pir_sensor = DigitalInputDevice(PIR_PIN)
pir2_sensor = DigitalInputDevice(PIR2_PIN)


motion_queue = Queue()
last_motion_time = 0
last_motion_time_2 = 0
    

def check_motion_1():
    global last_motion_time
    if pir_sensor.value:
        last_motion_time = time.time()
        if motion_queue.empty():
            motion_queue.put(True)
        return True
    return (time.time() - last_motion_time) <= MOTION_TO

def check_motion_2():
    global last_motion_time_2
    if pir2_sensor.value:
        last_motion_time_2 = time.time()
        return True
    return (time.time() - last_motion_time_2) <= MOTION_TO

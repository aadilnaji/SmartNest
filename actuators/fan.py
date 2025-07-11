from gpiozero import DigitalOutputDevice
from config import FAN_PIN, FAN_HOLD_TIME
import time

fan = DigitalOutputDevice(FAN_PIN)
manual_override = False
manual_state = False
last_auto_on = 0

def on():
    fan.on()

def off():
    fan.off()

def is_on():
    return fan.value == 1

def set_manual(state: bool):
    global manual_override, manual_state
    manual_override = True
    manual_state = state
    if state:
        on()
    else:
        off()

def clear_manual():
    global manual_override
    manual_override = False

def control(auto_triggered):
    global last_auto_on

    if auto_triggered:
        last_auto_on = time.time()

    if manual_override:
        if manual_state:
            on()
        else:
            off()
    else:
        if time.time() - last_auto_on <= FAN_HOLD_TIME:
            on()
        else:
            off()

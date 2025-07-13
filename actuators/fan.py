from gpiozero import DigitalOutputDevice
from config import FAN_PIN

fan = DigitalOutputDevice(FAN_PIN)


def on():
    fan.on()

def off():
    fan.off()

def is_on():
    return fan.value == 1

def set_manual(state: bool):
    if state:
        on()
    else:
        off()

def clear_manual():
    off()


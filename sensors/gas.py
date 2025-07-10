from gpiozero import DigitalInputDevice
from config import GAS_PIN

gas_sensor = DigitalInputDevice(GAS_PIN, pull_up=False)


def read():
    return int(not gas_sensor.value)
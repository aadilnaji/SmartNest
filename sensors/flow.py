from gpiozero import DigitalInputDevice
from config import FLOW_PIN, CALIB_FACTOR

pulse_count = 0


def flow_pulse():
    global pulse_count
    pulse_count += 1


flow_sensor = DigitalInputDevice(FLOW_PIN, pull_up=True)
flow_sensor.when_activated = flow_pulse


def get_flow_rate():
    global pulse_count
    rate = round(pulse_count / CALIB_FACTOR, 2)
    pulse_count = 0
    return rate
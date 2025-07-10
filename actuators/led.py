from gpiozero import PWMLED
from config import LED_PIN

led = PWMLED(LED_PIN)
led.value = 0.3


def on():
    led.value = 1.0


def off():
    led.value = 0.3


def is_on():
    return led.value >= 1.0
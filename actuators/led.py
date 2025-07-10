from gpiozero import PWMLED
from config import LED_PIN, LED2_PIN

led1 = PWMLED(LED_PIN)
led2 = PWMLED(LED2_PIN)

# Set LEDs to 30% brightness
led1.value = 0.3
led2.value = 0.3


#def on():
#    led.value = 1.0


#def off():
#    led.value = 0.3


#def is_on():
#    return led.value >= 1.0

def set_led1(on):
    led1.value = 1.0 if on else 0.3

def set_led2(on):
    led2.value = 1.0 if on else 0.3

def is_led1_on():
    return led1.value >= 1.0

def is_led2_on():
    return led2.value >= 1.0

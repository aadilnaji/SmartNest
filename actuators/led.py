from gpiozero import PWMLED
from config import LED_PIN, LED2_PIN, LED3_PIN, LED4_PIN

led1 = PWMLED(LED_PIN)
led2 = PWMLED(LED2_PIN)
led3 = PWMLED(LED3_PIN)
led4 = PWMLED(LED4_PIN)

# Set LEDs to 30% brightness
led1.value = 0.3
led2.value = 0.3


def set_led1(on):
    led1.value = 1.0 if on else 0.3

def set_led2(on):
    led2.value = 1.0 if on else 0.3
    
def set_led3(on):
    led3.on() if on else led3.off()

def set_led4(on):
    led4.on() if on else led4.off()

def is_led1_on():
    return led1.value >= 1.0

def is_led2_on():
    return led2.value >= 1.0

def is_led3_on():
    return led3.is_lit

def is_led4_on():
    return led4.is_lit

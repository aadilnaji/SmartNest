from gpiozero import AngularServo
from time import sleep
from config import SERVO_PIN, SERVO_WINDOW_PIN

# Door servo
door_servo = AngularServo(SERVO_PIN,
                          min_angle=0, max_angle=180,
                          min_pulse_width=0.5/1000,
                          max_pulse_width=2.5/1000)

# Window servo
window_servo = AngularServo(SERVO_WINDOW_PIN,
                            min_angle=0, max_angle=180,
                            min_pulse_width=0.5/1000,
                            max_pulse_width=2.5/1000)

# State tracking variable
window_open = False

def init_servo():
    door_servo.angle = 0
    door_servo.detach()
    window_servo.angle = 0
    window_servo.detach()
    global window_open
    window_open = False

def open_door():
    door_servo.angle = 180
    sleep(2)
    door_servo.detach()

def close_door():
    door_servo.angle = 0
    sleep(2)
    door_servo.detach()

def open_window():
    global window_open
    if not window_open:
        window_servo.angle = 180
        sleep(2)
        window_servo.detach()
        window_open = True

def close_window():
    global window_open
    if window_open:
        window_servo.angle = 0
        sleep(2)
        window_servo.detach()
        window_open = False

def is_window_open():
    return window_open

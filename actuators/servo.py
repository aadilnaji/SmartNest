from gpiozero import AngularServo
from time import sleep
from config import SERVO_PIN, SERVO2_PIN

# Door servo
door_servo = AngularServo(SERVO_PIN,
                           min_angle=0, max_angle=180,
                           min_pulse_width=0.5/1000,
                           max_pulse_width=2.5/1000)
# Window servo (use next available pin, e.g. SERVO_WINDOW_PIN in config)
window_servo = AngularServo(SERVO_WINDOW_PIN,
                             min_angle=0, max_angle=180,
                             min_pulse_width=0.5/1000,
                             max_pulse_width=2.5/1000)

def init_servo():
    door_servo.angle = 0
    door_servo.detach()
    window_servo.angle = 0
    window_servo.detach()


def open_door():
    door_servo.angle = 180
    sleep(2)
    door_servo.detach()


def close_door():
    door_servo.angle = 0
    sleep(2)
    door_servo.detach()


def open_window():
    window_servo.angle = 180
    sleep(2)
    window_servo.detach()


def close_window():
    window_servo.angle = 0
    sleep(2)
    window_servo.detach()

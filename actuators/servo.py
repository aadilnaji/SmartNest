# # FROM gpiozero import Servo
# from time import sleep
# from config import SERVO_PIN

# # Adjust GPIO pin number as needed
# servo = Servo(SERVO_PIN)  # GPIO23

# def open_door():
    # print("[DOOR] Unlocking door...")
    # servo.max()   # rotate to unlock position
    # sleep(2)
    # servo.min()   # back to locked position
    # sleep(0.5)
    # servo.detach()  # stop PWM to prevent jitter
    # print("[DOOR] Door locked again.")

# def init_servo():
    # servo.min()
    # servo.detach()  # start detached to avoid jitter

from gpiozero import AngularServo
from time import sleep
from config import SERVO_PIN

# Setup: Tune min_pulse_width and max_pulse_width as needed for your MG90S
servo = AngularServo(SERVO_PIN,
                     min_angle=0,
                     max_angle=180,
                     min_pulse_width=0.5/1000,
                     max_pulse_width=2.5/1000)  # 0.5ms to 2.5ms (you can adjust)
    
def open_door():
    print("[DOOR] Unlocking door...")
    servo.angle = 180  # Fully open position (adjust if needed)
    sleep(2)
    servo.detach()  # Stop PWM to prevent jitter
    print("[DOOR] Door unlocked.")

def close_door():
    print("[DOOR] Locking door...")
    servo.angle = 0  # Closed position
    sleep(2)
    servo.detach()
    print("[DOOR] Door locked.")

def init_servo():
    servo.angle = 0
    servo.detach()

from gpiozero import Servo
from time import sleep
from config import SERVO_PIN

# Adjust GPIO pin number as needed
servo = Servo(SERVO_PIN)  # GPIO23

def open_door():
    print("[DOOR] Unlocking door...")
    servo.max()  # Rotate to unlock
    sleep(2)
    servo.min()  # Return to lock
    print("[DOOR] Door locked again.")

import os
from dotenv import load_dotenv

load_dotenv()

# ThingsBoard
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_TOKEN")
BROKER_ADDR = "thingsboard.cloud"
BROKER_PORT = 1883

# Email
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

# Pins & Timing
FLOW_PIN      = 17
PIR_PIN       = 27
GAS_PIN       = 22
DHT_PIN       = 4
LED_PIN       = 18
SERVO_PIN     = 23
PIR2_PIN      = 24
LED2_PIN      = 15


MOTION_TO     = 5
CALIB_FACTOR  = 7.5

# Paths
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "captured_images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

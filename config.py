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
PIR2_PIN           = 24
FLOW_PIN           = 17
PIR_PIN            = 27
GAS_PIN            = 22
DHT_PIN            = 4
LED_PIN            = 18
LED2_PIN           = 15
LED3_PIN           = 0
LED4_PIN           = 2
ALERT_LED_PIN      = 26
SERVO_PIN          = 23
SERVO_WINDOW_PIN   = 3
FAN_PIN            = 14     # GPIO pin for relay

FAN_TEMP_THRESHOLD = 30     # Temp threshold
FAN_HOLD_TIME      = 10     # seconds the fan should stay on after detection

MOTION_TO          = 2      # Motion register delay   
CALIB_FACTOR       = 7.5    # Calibration factor for flow sensor

# Paths
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "captured_images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

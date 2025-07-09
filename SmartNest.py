import os
import time
import board
import datetime
import adafruit_dht
import json
import threading
from queue import Queue
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from picamera2 import Picamera2
import paho.mqtt.client as mqtt
import yagmail
from dotenv import load_dotenv
import signal
import sys

# === LOAD ENV VARIABLES ===
load_dotenv()
EMAIL_USER    = os.getenv("EMAIL_USER")
EMAIL_PASS    = os.getenv("EMAIL_PASS")
EMAIL_TO      = os.getenv("EMAIL_TO")
THINGSBOARD_TOKEN = os.getenv("THINGSBOARD_TOKEN")

# === CONFIGURATION ===
BROKER_ADDRESS = "thingsboard.cloud"
BROKER_PORT    = 1883

FLOW_PIN  = 17
PIR_PIN   = 27
GAS_PIN   = 22
DHT_PIN   = board.D4
LIGHT_PIN = 23  # This controls the LED
MOTION_TIMEOUT = 5
DHT_INTERVAL = 10
MQ_INTERVAL = 10
CALIB_FACTOR = 7.5

IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "captured_images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# === GLOBAL STATE ===
pulse_count = 0
last_dht_read = 0
last_mq_read = 0
last_motion_time = 0
light_state = False  # Store current state requested by dashboard
motion_event = False
readings_lock = threading.Lock()
motion_queue = Queue()

readings = {
    "flow_rate": 0.0,
    "temperature": None,
    "humidity": None,
    "air_quality": None,
    "motion": False,
}

# === HARDWARE SETUP ===
flow_sensor = DigitalInputDevice(FLOW_PIN, pull_up=True)
pir_sensor = DigitalInputDevice(PIR_PIN)
gas_sensor = DigitalInputDevice(GAS_PIN, pull_up=False)
dht_sensor = adafruit_dht.DHT11(DHT_PIN)
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
mailer = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
light = DigitalOutputDevice(LIGHT_PIN)

# === MQTT CLIENT SETUP ===
client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

# === CALLBACK HANDLERS ===
def flow_pulse():
    global pulse_count
    pulse_count += 1

flow_sensor.when_activated = flow_pulse

# === THREAD: MOTION HANDLER ===
def motion_worker():
    while True:
        motion_queue.get()
        image_path = capture_image()
        send_alert_email(image_path)
        with readings_lock:
            client.publish('v1/devices/me/telemetry', json.dumps({'event': 'image_captured'}))
            client.publish('v1/devices/me/telemetry', json.dumps({'event': 'email_sent'}))
        motion_queue.task_done()

# === FUNCTIONS ===
def send_alert_email(image_path):
    subject = f"[ALERT] Motion detected: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    mailer.send(to=EMAIL_TO, subject=subject, contents=["Motion detected!", image_path])

def capture_image():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_FOLDER, f"motion_{timestamp}.jpg")
    picam2.start()
    time.sleep(1)
    picam2.capture_file(image_path)
    picam2.stop()
    return image_path

def read_dht():
    try:
        return dht_sensor.temperature, dht_sensor.humidity
    except RuntimeError:
        return None, None

# === MQTT EVENT CALLBACKS ===
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing to RPC requests.")
    client.subscribe('v1/devices/me/rpc/request/+')

def on_message(client, userdata, msg):
    print(f"Received RPC message on topic {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        if data.get('method') == 'setLight':
            global light_state
            light_state = bool(data.get('params'))
        elif data.get('method') == 'openDoor':
            print("Door control RPC received:", data)
            # Door control logic here
    except Exception as e:
        print("Error handling RPC message:", e)


client.on_connect = on_connect
client.on_message = on_message

# === CLEANUP HANDLER ===
def exit_gracefully(signum, frame):
    print("\n[EXIT] Cleaning up GPIO and exiting...")
    dht_sensor.exit()
    picam2.close()
    client.loop_stop()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

# === MAIN LOOP ===
def main_loop():
    global pulse_count, last_dht_read, last_mq_read, last_motion_time
    last_flow_time = time.time()

    try:
        while True:
            now = time.time()
            with readings_lock:
                # Flow rate every 1 second
                if now - last_flow_time >= 1.0:
                    readings['flow_rate'] = round(pulse_count / CALIB_FACTOR, 2)
                    pulse_count = 0
                    last_flow_time = now

                # DHT every interval
                if now - last_dht_read >= DHT_INTERVAL:
                    t, h = read_dht()
                    readings['temperature'] = t
                    readings['humidity'] = h
                    last_dht_read = now

                # MQ135 every interval
                if now - last_mq_read >= MQ_INTERVAL:
                    readings['air_quality'] = int(gas_sensor.value)
                    last_mq_read = now

                # Motion detection
                if pir_sensor.value:
                    readings['motion'] = True
                    last_motion_time = now
                    if motion_queue.empty():
                        motion_queue.put(True)
                else:
                    readings['motion'] = False

                # Light control logic
                motion_active = (now - last_motion_time) <= MOTION_TIMEOUT
                
                if light_state:
                    # RPC command to turn on light
                    light.on()
                elif motion_active:
                    # Keep light on during motion timeout period
                    light.on()
                else:
                    # Turn off light (no RPC command and no recent motion)
                    light.off()

                # Publish latest state
                client.publish('v1/devices/me/telemetry', json.dumps(readings))
            time.sleep(0.5)

    except KeyboardInterrupt:
        exit_gracefully(None, None)

# === RUN ===
print("Starting system with LED control via ThingsBoard and motion events...")
client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
threading.Thread(target=motion_worker, daemon=True).start()
client.loop_start()
main_loop()


import adafruit_dht
import board
import time
from config import DHT_PIN

dht_sensor = adafruit_dht.DHT11(board.D4)

# Wait for sensor to stabilize
time.sleep(2)

def read():
    try:
        return dht_sensor.temperature, dht_sensor.humidity
    except RuntimeError:
        return None, None

def cleanup():
    try:
        dht_sensor.exit()
    except Exception:
        pass

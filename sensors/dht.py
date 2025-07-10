import adafruit_dht
import board
from config import DHT_PIN

dht_sensor = adafruit_dht.DHT11(board.D4)


def read():
    try:
        return dht_sensor.temperature, dht_sensor.humidity
    except RuntimeError:
        return None, None


def cleanup():
    dht_sensor.exit()
import json
import paho.mqtt.client as mqtt
from config import THINGSBOARD_TOKEN, BROKER_ADDR, BROKER_PORT
from actuators.servo import open_door

client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

light_state = False


def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing to RPC requests.")
    client.subscribe('v1/devices/me/rpc/request/+')


def on_message(client, userdata, msg):
    global light_state
    try:
        data = json.loads(msg.payload.decode())
        if data.get('method') == 'setLight':
            light_state = bool(data.get('params'))
        elif data.get('method') == 'openDoor':
            print("Door control RPC received:", data)
            open_door()
            publish_telemetry({"event": "manual_door_opened"})
    except Exception as e:
        print("Error handling RPC message:", e)


def publish_telemetry(payload):
    client.publish('v1/devices/me/telemetry', json.dumps(payload))


def start():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDR, BROKER_PORT, 60)
    client.loop_start()


def stop():
    client.loop_stop()

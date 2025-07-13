import json
import paho.mqtt.client as mqtt

from config import THINGSBOARD_TOKEN, BROKER_ADDR, BROKER_PORT
from actuators.servo import open_door, close_door, open_window, close_window
from actuators.fan import set_manual, clear_manual
from actuators.led import set_led3, set_led4

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

# State variables for RPC logic
light_state = False
light_state2 = False
light_state3 = False
light_state4 = False

fan_manual_override = False
fan_manual_state = False
window_manual_override = False
window_manual_state = False

latest_temperature = None
latest_air_quality = 0


# RPC handlers

def handle_set_light(params):
    global light_state
    light_state = bool(params)

def handle_set_light2(params):
    global light_state2
    light_state2 = bool(params)

def handle_set_light3(params):
    global light_state3
    light_state3 = bool(params)

def handle_set_light4(params):
    global light_state4
    light_state4 = bool(params)

def handle_set_fan(params):
    global fan_manual_override, fan_manual_state

    if params is None:
        clear_manual()
        fan_manual_override = False
        fan_manual_state = False
    else:
        set_manual(bool(params))
        fan_manual_override = True
        fan_manual_state = bool(params)

    publish_telemetry({
        "event": "fan_manual_set",
        "state": params
    })

def handle_open_door(params):
    if params:
        open_door()
        publish_telemetry({"event": "manual_door_opened"})
    else:
        close_door()
        publish_telemetry({"event": "manual_door_closed"})

def handle_open_window(params):
    if params:
        open_window()
        publish_telemetry({"event": "manual_window_opened"})
    else:
        close_window()
        publish_telemetry({"event": "manual_window_closed"})


# Method mapping for RPC requests

rpc_handlers = {
    "setLight": handle_set_light,
    "setLight2": handle_set_light2,
    "setLight3": handle_set_light3,
    "setLight4": handle_set_light4,
    "setFan": handle_set_fan,
    "openDoor": handle_open_door,
    "openWindow": handle_open_window,
}


# MQTT Callbacks

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing to RPC requests.")
    client.subscribe('v1/devices/me/rpc/request/+')


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        method = data.get('method')
        params = data.get('params')

        handler = rpc_handlers.get(method)
        if handler:
            handler(params)
        else:
            print(f"[MQTT] Unrecognized method: {method}")

    except Exception as e:
        print(f"[MQTT ERROR] Handling message: {e}")


# Publish Telemetry

def publish_telemetry(payload):
    global latest_temperature, latest_air_quality

    if 'temperature' in payload:
        latest_temperature = payload['temperature']
    if 'air_quality' in payload:
        latest_air_quality = payload['air_quality']

    client.publish('v1/devices/me/telemetry', json.dumps(payload))


# MQTT Lifecycle

def start():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDR, BROKER_PORT, 60)
    client.loop_start()


def stop():
    client.loop_stop()

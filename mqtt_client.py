import json
import paho.mqtt.client as mqtt
from config import THINGSBOARD_TOKEN, BROKER_ADDR, BROKER_PORT
from actuators.servo import open_door, close_door
from actuators.fan import set_manual, clear_manual
from actuators.led import set_led3, set_led4


client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

light_state = False
light_state2 = False
light_state3 = False
light_state4 = False

fan_manual_override = False
fan_manual_state = False


def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing to RPC requests.")
    client.subscribe('v1/devices/me/rpc/request/+')

        
def on_message(client, userdata, msg):
    global light_state, light_state2, light_state3, light_state4, fan_manual_override, fan_manual_state
    try:
        data = json.loads(msg.payload.decode())
        method = data.get('method')
        params = data.get('params')

        if method == 'setLight':
            light_state = bool(params)
        elif method == 'setLight2':
            light_state2 = bool(params)
        if method == 'setLight3':
            light_state3 = bool(params)
        elif method == 'setLight4':
            light_state4 = bool(params)
        elif method == 'setFan':
            val = params
            if val is None:
                clear_manual()
                fan_manual_override = False
                fan_manual_state = False
            else:
                set_manual(bool(val))
                fan_manual_override = True
                fan_manual_state = bool(val)
            publish_telemetry({"event": "fan_manual_set", "state": val})
        elif method == 'openDoor':
            if params:
                open_door()
                print("Door open RPC received:", data)
                publish_telemetry({"event": "manual_door_opened"})
            else :
                close_door()
                print("Door close RPC recieved", data)
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

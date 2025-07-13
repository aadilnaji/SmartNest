from mfrc522 import SimpleMFRC522
from actuators.servo import open_door, close_door
import time
import threading
from mqtt_client import publish_telemetry

reader = SimpleMFRC522()
AUTHORIZED_UIDS = ['1091744629187', 'ADD_YOUR_UIDS_HERE']  

LOCK_DELAY = 6  # seconds

def _auto_lock():
    time.sleep(LOCK_DELAY)
    close_door()
    publish_telemetry({"event": "door_auto_locked"})

def rfid_loop():
    print("[RFID] RFID reader started. Waiting for card...")
    while True:
        try:
            id, text = reader.read()
            print(f"[RFID] Card detected. UID: {id}")
            if str(id) in AUTHORIZED_UIDS:
                print("[RFID] Access granted. Opening door.")
                open_door()
                publish_telemetry({"event": "rfid_door_unlocked", "uid": str(id)})
                threading.Thread(target=_auto_lock, daemon=True).start()
            else:
                print("[RFID] Access denied.")
            time.sleep(1)
        except Exception as e:
            print(f"[RFID] Error: {e}")
            time.sleep(1)



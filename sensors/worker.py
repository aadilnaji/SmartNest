import threading
import time
from mqtt_client import publish_telemetry

class SensorWorker(threading.Thread):
    def __init__(self, name, interval, read_function, telemetry_key=None, telemetry_key2=None):
        super().__init__(name=name)
        self.interval = interval
        self.read_function = read_function
        self.telemetry_key = telemetry_key
        self.telemetry_key2 = telemetry_key2
        self.daemon = True
        self._stop_event = threading.Event()

    def run(self):
        print(f"[THREAD] {self.name} started with interval {self.interval}s")
        while not self._stop_event.is_set():
            try:
                result = self.read_function()

                if result is not None:
                    if self.telemetry_key2 and isinstance(result, tuple):
                        payload = {
                            self.telemetry_key: result[0],
                            self.telemetry_key2: result[1]
                        }
                    else:
                        payload = {
                            self.telemetry_key: result
                        }
                    publish_telemetry(payload)

            except Exception as e:
                print(f"[ERROR] {self.name}: {e}")

            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

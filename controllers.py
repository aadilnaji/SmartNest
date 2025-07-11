import time
from actuators.fan import on as fan_on, off as fan_off
from actuators.fan import set_manual as fan_set_manual, clear_manual as fan_clear_manual
from actuators.servo import open_door, close_door, open_window, close_window
from config import FAN_HOLD_TIME, FAN_TEMP_THRESHOLD

class Controller:
    def __init__(self):
        self.last_fan_auto = 0

    def handle_temperature(self, temp):
        if temp is not None and temp >= FAN_TEMP_THRESHOLD:
            self.last_fan_auto = time.time()
            self._apply_fan_state(auto=True)

    def handle_air_quality(self, aq):
        if aq == 1:
            self.last_fan_auto = time.time()
            self._apply_fan_state(auto=True)

    def _apply_fan_state(self, auto=False, manual=None):
        # manual: True/False or None
        if manual is not None:
            fan_set_manual(manual)
            return
        # auto control based on last trigger
        if time.time() - self.last_fan_auto <= FAN_HOLD_TIME:
            fan_on()
        else:
            fan_off()

    def set_fan_rpc(self, params):
        if params is None:
            fan_clear_manual()
            self._apply_fan_state()
        else:
            self._apply_fan_state(manual=bool(params))
        publish_telemetry({"event": "fan_manual_set", "state": params})

    def set_door_rpc(self, open_flag):
        if open_flag:
            open_door()
        else:
            close_door()

    def set_window_rpc(self, open_flag):
        if open_flag:
            open_window()
        else:
            close_window()
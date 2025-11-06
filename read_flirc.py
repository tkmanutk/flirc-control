#!/usr/bin/env python3
import evdev, json, sys

# open your Flirc input device
device = evdev.InputDevice("/dev/input/by-id/usb-flirc.tv_flirc_B657C57351503639304A2020FF0C171C-if01-event-kbd")

for event in device.read_loop():
    if event.type == evdev.ecodes.EV_KEY:
        key_name = evdev.ecodes.KEY[event.code]
        payload = {
            "code": key_name,   # e.g. KEY_1, KEY_2
            "value": event.value  # 1=press, 2=repeat, 0=release
        }
        print(json.dumps(payload))
        sys.stdout.flush()

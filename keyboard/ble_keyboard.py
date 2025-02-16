# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example acts as a keyboard to peer devices.
"""

# import board
import sys
import time
import select

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService


# Use default HID descriptor
hid = HIDService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="None"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()

ble = adafruit_ble.BLERadio()
if ble.connected:
    for c in ble.connections:
        c.disconnect()

print("advertising")
ble.start_advertising(advertisement, scan_response)

allowed_command_characters = ['\x1b', '\x7f', '\x07', '\x08', '\x09', '\x0a', '\x0d']

k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)

# Define key repeat parameters
initial_delay = 0.5   # delay before auto-repeat starts (in seconds)
repeat_interval = 0.1   # interval between repeats (in seconds)

# Reset key hold tracking upon connection
current_key = None
is_held = False
key_press_time = time.monotonic()
last_key_time = time.monotonic()
last_repeat_time = time.monotonic()
hold_refresh_threshold = 0.25  # time within which a repeated key event indicates a hold
release_timeout = 0.3         # time after which, without new events, the key is considered released

while True:
    while not ble.connected:
        time.sleep(0.1)
    print("Start typing:")
    # Reset key hold tracking upon connection
    current_key = None
    is_held = False
    key_press_time = time.monotonic()
    last_key_time = time.monotonic()
    last_repeat_time = time.monotonic()
    while ble.connected:
        now = time.monotonic()
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            c = sys.stdin.read(1)
            if c:
                if c == "\x1b":
                    # Handle escape sequence for arrow keys and delete
                    time.sleep(0.01)  # brief pause to allow full sequence
                    if select.select([sys.stdin], [], [], 0)[0]:
                        seq = sys.stdin.read(2)
                        if seq == "[A":
                            print("Sending UP arrow")
                            k.send(Keycode.UP_ARROW)
                            key_val = Keycode.UP_ARROW
                        elif seq == "[B":
                            print("Sending DOWN arrow")
                            k.send(Keycode.DOWN_ARROW)
                            key_val = Keycode.DOWN_ARROW
                        elif seq == "[C":
                            print("Sending RIGHT arrow")
                            k.send(Keycode.RIGHT_ARROW)
                            key_val = Keycode.RIGHT_ARROW
                        elif seq == "[D":
                            print("Sending LEFT arrow")
                            k.send(Keycode.LEFT_ARROW)
                            key_val = Keycode.LEFT_ARROW
                        elif seq.startswith("[3"):
                            extra = sys.stdin.read(1)
                            seq += extra
                            if seq == "[3~":
                                print("Sending DELETE")
                                k.send(Keycode.DELETE)
                                key_val = Keycode.DELETE
                            else:
                                key_val = None
                        else:
                            print(f"Unknown escape sequence: {seq}")
                            key_val = None

                        if key_val is not None:
                            # If the same key is observed within the threshold, mark it as held
                            if current_key == key_val and (now - last_key_time) <= hold_refresh_threshold:
                                is_held = True
                            else:
                                current_key = key_val
                                is_held = False
                                key_press_time = now
                            last_key_time = now
                        # No additional output for escape sequences as they've been handled
                    else:
                        # No additional chars; treat as normal character
                        sys.stdout.write(c)
                        kl.write(c)
                        current_key = c
                        is_held = False
                        key_press_time = now
                        last_key_time = now
                else:
                    if ord(c) >= 32 or c in allowed_command_characters:
                        sys.stdout.write(c)
                        kl.write(c)
                    # For normal keys, if the same key is received quickly, mark as held
                    if current_key == c and (now - last_key_time) <= hold_refresh_threshold:
                        is_held = True
                    else:
                        current_key = c
                        is_held = False
                        key_press_time = now
                    last_key_time = now
                # Reset auto-repeat timer on physical key event
                last_repeat_time = now
        else:
            # No new physical event
            if (is_held and current_key is not None):
                if ((now - key_press_time) >= initial_delay and (now - last_repeat_time) >= repeat_interval):
                    if isinstance(current_key, int):
                        k.send(current_key)
                    else:
                        sys.stdout.write(current_key)
                        kl.write(current_key)
                    last_repeat_time = now
            # If no key event for a while, consider the key released
            if ((now - last_key_time) >= release_timeout):
                is_held = False
                current_key = None
        time.sleep(0.01)
    ble.start_advertising(advertisement)
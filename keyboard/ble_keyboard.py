# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example acts as a keyboard to peer devices.
"""

# import board
import sys
import time

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
    software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
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
while True:
    while not ble.connected:
        pass
    print("Start typing:")
    while ble.connected:
        c = sys.stdin.read(1)
        if c == "\x1b":
            # Detected start of an escape sequence, likely an arrow key
            seq = sys.stdin.read(2)  # Read the next two characters
            if seq == "[A":
                print("Sending UP arrow")
                k.send(Keycode.UP_ARROW)
            elif seq == "[B":
                print("Sending DOWN arrow")
                k.send(Keycode.DOWN_ARROW)
            elif seq == "[C":
                print("Sending RIGHT arrow")
                k.send(Keycode.RIGHT_ARROW)
            elif seq == "[D":
                print("Sending LEFT arrow")
                k.send(Keycode.LEFT_ARROW)
            elif seq == "[3~":
                print("Sending DELETE")
                k.send(Keycode.DELETE)
            else:
                print(f"Unknown escape sequence: {seq}")
            continue
        else:
            # Filter out unwanted control characters except newline, carriage return, and tab
            if ord(c) < 32 and c not in allowed_command_characters:
                continue
            sys.stdout.write(c)
            kl.write(c)

        time.sleep(0.1)
    ble.start_advertising(advertisement)
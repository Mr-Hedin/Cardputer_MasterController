'''hid_keyboard.py - Stub for HID keyboard functionality using Cardputer keyboard library.

This module attaches the serial interface and routes input from stdin to the HID output.
'''

import asyncio
import sys
import cardputer_keyboard
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

try:
    import select
    has_select = True
except ImportError:
    has_select = False

async def run_hid_keyboard():
    # Attach serial interface using cardputer_keyboard module
    cardputer_keyboard.attach_serial()

    # Initialize HID keyboard using adafruit HID library
    keyboard = Keyboard()
    layout = KeyboardLayoutUS(keyboard)

    print("HID Keyboard running. Waiting for input...")

    try:
        while True:
            if has_select:
                # Use select to check if sys.stdin has data ready (non-blocking wait up to 0.1 sec)
                ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                if ready:
                    line = sys.stdin.readline()
                else:
                    await asyncio.sleep(0)
                    continue
            else:
                # Fallback if select is not available (this may block, so we yield briefly first)
                await asyncio.sleep(0.1)
                line = sys.stdin.readline()

            if not line:
                continue
            line = line.rstrip('\n')
            if line:
                print(f"Received input: {line}")
                layout.write(line)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting HID keyboard.")

if __name__ == '__main__':
    asyncio.run(run_hid_keyboard()) 
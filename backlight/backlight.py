import board
import displayio
import terminalio
from adafruit_display_text import label
import time
import sys
import cardputer_keyboard


def get_slider_str(brightness, length=20):
    # Build a text slider reflecting brightness (0.0 to 1.0)
    num_pluses = int(round(brightness * length))
    if num_pluses > length:
        num_pluses = length
    num_minuses = length - num_pluses
    return "[" + ("=" * num_pluses) + ("-" * num_minuses) + "]"

def set_backlight_level(brightness):
    # Clamp brightness between 0.0 and 1.0
    if brightness < 0.0:
        brightness = 0.0
    if brightness > 1.0:
        brightness = 1.0
    board.DISPLAY.brightness = brightness
    return brightness

def display_backlight_menu():
    # Create the main display group
    main_group = displayio.Group()

    # Create a full-screen black background
    splash_bitmap = displayio.Bitmap(board.DISPLAY.width, board.DISPLAY.height, 1)
    splash_palette = displayio.Palette(1)
    splash_palette[0] = 0x000000  # black
    bg_sprite = displayio.TileGrid(splash_bitmap, pixel_shader=splash_palette, x=0, y=0)
    main_group.append(bg_sprite)


    # Calculate positions - adjust y_start to account for status bar
    line_height = terminalio.FONT.get_bounding_box()[1]
    spacing = 4
    y_start = 40  # Increased to account for status bar

    # Create labels
    title_label = label.Label(
        terminalio.FONT,
        text="Backlight Control",
        color=0x00FF00,
        x=10,
        y=y_start
    )
    main_group.append(title_label)

    brightness_label = label.Label(
        terminalio.FONT,
        text="",  # Will be updated in the loop
        color=0x00FF00,
        x=10,
        y=y_start + line_height + spacing
    )
    main_group.append(brightness_label)

    instructions_label = label.Label(
        terminalio.FONT,
        text="Use LEFT/RIGHT or A/D to adjust",
        color=0x007700,
        x=10,
        y=y_start + (line_height + spacing) * 2
    )
    main_group.append(instructions_label)

    exit_label = label.Label(
        terminalio.FONT,
        text="Press ENTER to exit",
        color=0x007700,
        x=10,
        y=y_start + (line_height + spacing) * 3
    )
    main_group.append(exit_label)

    # Show the menu
    board.DISPLAY.root_group = main_group

    # Get initial brightness
    current = board.DISPLAY.brightness
    
    # Attach keyboard
    cardputer_keyboard.attach_serial()

    while True:
        # Update brightness display
        slider = get_slider_str(current)
        brightness_text = f"Brightness: {slider} {int(current*100)}%"
        brightness_label.text = brightness_text


        # Check for user input
        c = sys.stdin.read(1)
        if c:
            if c == '\x1b':
                seq = sys.stdin.read(2)
                if seq == "[C":  # Right arrow
                    current = set_backlight_level(current + 0.05)
                elif seq == "[D":  # Left arrow
                    current = set_backlight_level(current - 0.05)
            elif c.lower() == 'd':  # d key for right
                current = set_backlight_level(current + 0.05)
            elif c.lower() == 'a':  # a key for left
                current = set_backlight_level(current - 0.05)
            elif c in ['\r', '\n']:  # Enter key
                break

        time.sleep(0.05)

if __name__ == "__main__":
    display_backlight_menu()


'''menu_interface.py - Stub for a terminal-style selection menu interface.

This module provides a simple menu that supports highlighted selection, pagination, and scrolling for long entries.
Scrolling definitely doesn't work.
'''

def display_menu(options):
    """Display a list of options with highlighted selection and pagination using displayio."""
    import board
    import displayio
    import terminalio
    from adafruit_display_text import label
    import time
    import cardputer_keyboard
    import sys

    # Create the main display group
    main_group = displayio.Group()

    # Create a full-screen black background
    splash_bitmap = displayio.Bitmap(board.DISPLAY.width, board.DISPLAY.height, 1)
    splash_palette = displayio.Palette(1)
    splash_palette[0] = 0x000000  # black
    bg_sprite = displayio.TileGrid(splash_bitmap, pixel_shader=splash_palette, x=0, y=0)
    main_group.append(bg_sprite)


    # Calculate line spacing and visible lines, accounting for the status bar height
    line_height = terminalio.FONT.get_bounding_box()[1]  # font height
    spacing = 2
    line_spacing = line_height + spacing
    status_bar_height = 20  # Height of status bar area
    visible_count = (board.DISPLAY.height - status_bar_height) // line_spacing

    # Initialize pagination and selection
    selected_index = 0
    page_offset = 0

    # Create label objects for each visible line (reuse them during updates)
    labels = []
    for i in range(visible_count):
        option_index = page_offset + i
        if option_index < len(options):
            if option_index == selected_index:
                text = "> " + options[option_index]
                text_color = 0x00FF00
            else:
                text = "  " + options[option_index]
                text_color = 0x007700
        else:
            text = ""
            text_color = 0x007700
        lbl = label.Label(
            terminalio.FONT, 
            text=text, 
            color=text_color, 
            x=2, 
            y=status_bar_height + i * line_spacing + line_height
        )
        labels.append(lbl)
        main_group.append(lbl)

    display = board.DISPLAY
    # Show the menu
    display.root_group = main_group

    print("Use 'w' to move up, 's' to move down, and press Enter to select the highlighted option.")
    cardputer_keyboard.attach_serial()

    # Interactive loop using non-blocking serial input and scrolling for long highlighted text
    last_scroll_time = time.monotonic()
    scroll_delay = 0.3
    scroll_offset = 0
    char_width = terminalio.FONT.get_bounding_box()[0]
    available_chars = (display.width - 4) // char_width
    available_total = available_chars

    while True:
        current_time = time.monotonic()
        # Recalculate available characters for option text (not including prefix) each loop iteration
        available_chars = (display.width - 4) // char_width
        available_total = available_chars

        # Determine the text portion to scroll for the highlighted option
        current_text = options[selected_index]
        if ':' in current_text:
            static, sep, scroll_text = current_text.partition(':')
            static = static + sep
            available_for_scroll = available_total - len(static) - 1  # one space between static and scroll
            if available_for_scroll < 0:
                available_for_scroll = 0
            text_to_scroll = scroll_text.strip()
        else:
            text_to_scroll = current_text
            available_for_scroll = available_total

        # Update scroll offset if the text to scroll exceeds available space
        if len(text_to_scroll) > available_for_scroll and (current_time - last_scroll_time >= scroll_delay):
            last_scroll_time = current_time
            scroll_offset = (scroll_offset + 1) % (len(text_to_scroll) + 3)  # add gap of 3 spaces

        # Update all visible labels with potential scrolling for the highlighted option
        for i in range(visible_count):
            option_index = page_offset + i
            if option_index < len(options):
                if option_index == selected_index:
                    prefix = "> "
                    text = options[option_index]
                    # If the text has a colon, keep the static part and scroll only the remainder
                    if ':' in text:
                        static, sep, scroll_text = text.partition(':')
                        static = static + sep
                        available_for_scroll = available_total - len(static) - 1
                        if available_for_scroll < 0:
                            available_for_scroll = 0
                        if len(scroll_text.strip()) > available_for_scroll:
                            extended = scroll_text.strip() + "   "
                            display_scroll = extended[scroll_offset:scroll_offset+available_for_scroll]
                        else:
                            display_scroll = scroll_text.strip()
                        display_text = static + " " + display_scroll
                    else:
                        if len(text) > available_total:
                            extended = text + "   "
                            display_text = extended[scroll_offset:scroll_offset+available_total]
                        else:
                            display_text = text
                    labels[i].text = prefix + display_text
                    labels[i].color = 0x00FF00
                else:
                    prefix = "  "
                    text = options[option_index]
                    if len(text) > available_total:
                        display_text = text[:available_total]
                    else:
                        display_text = text
                    labels[i].text = prefix + display_text
                    labels[i].color = 0x007700
            else:
                labels[i].text = ""

        # Non-blocking check for user input
        user_input = sys.stdin.read(1)
        if user_input:
            # Check for arrow key escape sequence
            if user_input == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    user_input = "w"
                elif seq == "[B":
                    user_input = "s"

            if user_input == "w":
                if selected_index > 0:
                    selected_index -= 1
                    if selected_index < page_offset:
                        page_offset = selected_index
                    scroll_offset = 0
            elif user_input == "s":
                if selected_index < len(options) - 1:
                    selected_index += 1
                    if selected_index >= page_offset + visible_count:
                        page_offset = selected_index - visible_count + 1
                    scroll_offset = 0
            elif user_input in ["\n", "\r"]:
                break

        time.sleep(0.05)

    print("Selected option:", options[selected_index])
    time.sleep(1)  # Pause briefly before ending the menu
    return selected_index

if __name__ == '__main__':
    # Example usage of the menu interface
    sample_options = [
        'Option 1: This is a long description that might need scrolling or truncation',
        'Option 2',
        'Option 3',
        'Option 4'
    ]
    display_menu(sample_options) 
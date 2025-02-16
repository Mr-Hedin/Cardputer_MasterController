from interface_modules import menu_interface
import command_registry as command_registry
from battery.battery import get_battery_voltage

def mount_sdcard():
    """Mount the SD card using SPI and mount it at '/sd'."""
    import digitalio
    import board
    import adafruit_sdcard
    import storage
    import os
    cs = digitalio.DigitalInOut(board.SD_CS)
    spi = board.SD_SPI()
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    print("SD Card mounted")
    try:
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, "/sd", readonly=False)
        print("SD Card mounted at /sd")
        print(os.listdir("/sd"))
        return sdcard
    except Exception as e:
        print(f"Error mounting SD Card: {e}")
sdcard = mount_sdcard()




def display_command_menu(commands):
    return menu_interface.display_command_menu(commands)

def sample_action():
    print("Sample action executed!")

def sample_action2(param1, param2):
    print(f"Sample action 2 executed with {param1} and {param2}")

# Register commands into the command registry
device_name = "cardputer"
registry = command_registry.get_registry(device_name)
command_registry.register_command(command_registry.Command("Sample Command: Do something", "Executes a sample action", sample_action), registry)
command_registry.register_command(command_registry.Command("Battery Voltage: Get battery voltage", "Get the current battery voltage as a percentage", get_battery_voltage), registry)
# Retrieve all commands
commands = registry

# Write the command list to a file (for AI function calling or other uses)
device_name = "cardputer"
#mount_sdcard()
command_registry.write_commandlist_to_file(device_name, commands, registry)
print(f"Command list written to {device_name}_commandlist.json")

# Read back the command list from the file (demonstration purpose)
commandlist_from_file = registry
print("Command list loaded from file:", commandlist_from_file)

# Display the list of commands using the menu interface and execute the selected command
selected_command = display_command_menu(commands)
print("Executing selected command...")
selected_command.execute()
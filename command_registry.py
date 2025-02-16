"""Command Registry Module.

This module provides a global command registry used to register and manage command objects.
Each command is defined by a name, description, and a callback function to execute.
Eventually this will be used to register commands from other modules for the AI to use via function calling.
"""
import json
import os
import storage
import board
import adafruit_sdcard



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
    


class Command:
    def __init__(self, name, description, callback, args=None, kwargs=None):
        """
        Initialize a Command.
        name: The display name or text of the command.
        description: A short description.
        callback: A function to call when the command is executed.
        args: A list of arguments to pass to the callback function.
        kwargs: A dictionary of keyword arguments to pass to the callback function.
        """
        self.name = name
        self.description = description
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        self.callback(*self.args if self.args else [], **self.kwargs if self.kwargs else {})


def write_commandlist_to_file(device_name, commands):
    """Write a commandlist to a file on the SD card."""
    try:
        filepath = f"/sd/{device_name}_commandlist.json"
        if not (filepath) in os.listdir("/sd"):
            with open(filepath, "w") as f:
                f.write(prepare_commandlist_for_ai(commands))
    except Exception as e:
        print(f"Error writing commandlist to file: {e}")


def get_registry(device_name):
    """Read a commandlist from a file on the SD card."""
    filepath = f"/sd/{device_name}_commandlist.json"
    if not (filepath) in os.listdir("/sd"):
        return None
    with open(filepath, "r") as f:
        command_registry = json.load(f)
    return command_registry
    

def register_command(command, command_registry):
    """Register a new command into the global registry."""
    command_registry[command.name] = command


def get_commands(device_name):
    """Return the list of registered commands."""
    command_registry = get_registry(device_name)
    return list(command_registry.values())


def clear_commands(device_name):
    """Clear the registered commands."""
    command_registry = get_registry(device_name)
    command_registry.clear()
    write_commandlist_to_file(device_name, command_registry)

def add_command_args(command, args):
    """Add arguments to a command."""
    command.args = args


def add_keyword_args(command, kwargs):
    """Add keyword arguments to a command."""
    command.kwargs = kwargs


def prepare_commandlist_for_ai(commands):
    """Format a list of commands for AI function calling in OpenAI tools format."""
    tools = []
    
    for command in commands:
        parameters = {}
        if command.args:
            parameters["type"] = "object"
            parameters["properties"] = {}
            for i, arg in enumerate(command.args):
                parameters["properties"][f"arg{i}"] = {
                    "type": "string",
                    "description": f"Argument {i} for {command.name}"
                }
            parameters["required"] = [f"arg{i}" for i in range(len(command.args))]
        elif command.kwargs:
            parameters["type"] = "object"
            parameters["properties"] = {
                k: {
                    "type": "string",
                    "description": f"Keyword argument {k} for {command.name}"
                } for k in command.kwargs
            }
            parameters["required"] = list(command.kwargs.keys())
        else:
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        parameters["additionalProperties"] = False

        tools.append({
            "type": "function",
            "function": {
                "name": command.name,
                "description": command.description,
                "parameters": parameters,
                "strict": True
            }
        })
    
    return json.dumps({"tools": tools})



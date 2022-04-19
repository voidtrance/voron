# Installing Klipper Extensions

Klipper extensions are placed in _~/klipper/klippy/extras_.

# Custom Extension Information
The extensions listed below are extensions that I've modified or enhanced.

## gcode_shell_command.py

The original extesion is part of the Kiauh repo (https://github.com/th33xitus/kiauh/blob/master/resources/gcode_shell_command.py).
I've modified it to add support for custom GCode execution on either success or failure:

```
[gcode_shell_command COMMAND]
command:
#   The command line to be executed. This option is required.
#timeout: 2.0
#   The amount of time (in seconds) to wait before forcefully
#   terminating the command.
#verbose: True
#   Enable verbose output to the console.
#success:
#   A list of G-Code commands to execute if the command
#   completes successfully. If this option is not present
#   nothing will be executed.
#failure:
#   A list of G-Code commands to execute if the command
#   does not complete successfully. If this option is not
#   present nothing will be executed.
```
### Example
```
[gcode_shell_command my_command]
command: echo my_command executing
success:
    M117 my_command executed successfully.
failure:
    M117 my_command failed.

[gcode_macro exec_my_command]
gcode:
    RUN_SHELL_COMMAND CMD=my_command
```

#### __WARNING__: Infinite Loops

Since the G-Code executed on success/failure can be arbitrary, on top of
all the other issues resulting from using external commands, it is now possible to
create an infinite loop that will prevent the printer from continuing.

For example, the following will cause an infinite loop:

```
[gcode_shell_command my_command]
command: echo my_command executing
success:
    exec_my_command

[gcode_macro exec_my_command]
gcode:
    RUN_SHELL_COMMAND CMD=my_command
```
# Installing Klipper Extensions

Klipper extensions are placed in __~/klipper/klippy/extras__.

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


# Installing Klipper Extensions

Klipper extensions are placed in _~/klipper/klippy/extras_.

# Custom Extension Information
The extensions listed below are extensions that I've modified or enhanced.

## gcode_shell_command.py

The original extesion is part of the Kiauh repo (https://github.com/th33xitus/kiauh/blob/master/resources/gcode_shell_command.py).
I've modified it to add support for custom GCode execution on either success or failure:

```
[gcode_shell_command COMMAND]
#value_<var>: <value>
#   Output value that can be updated by the command. <value>
#   serves as a default.
command:
#   The command line to be executed. This option is required.
#   The command can update the values for any of the value_*
#   variables above. In order to do so, the command should
#   output the update value in the following format:
#      VALUE_UPDATE:<var>=<value>
#   Only one value can be updated on a single line. The updated
#   values are processes as strings.
#timeout: 2.0
#   The amount of time (in seconds) to wait before forcefully
#   terminating the command.
#verbose: True
#   Enable verbose output to the console.
#success:
#   A list of G-Code commands to execute if the command
#   completes successfully. If this option is not present
#   nothing will be executed.
#   This section is evaluated as a template and can
#   reference the value_* values.
#failure:
#   A list of G-Code commands to execute if the command
#   does not complete successfully. If this option is not
#   present nothing will be executed.
#   This section is evaluated as a template and can
#   reference the value_* values.
```
### Examples
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

```
[gcode_shell_command my_command]
value_var1: 0
command: echo "VALUE_UPDATE:var1=10"
success:
    {action_respnd_info("var1=%s" % var1)}
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

## led_interpolate.py

A small extension that can be used to smootly transition (interpolate) RGB(W)
LEDs between colors.

While planning/working on adding LEDs to my printer case, I wanted to be able
to have the LEDs dim. However, rather than just setting the color and have the
dimming happen immediately, I thought it will be much nicer if they transition
smoothly.

The led_interpolate.py extension does that. It will smoothly transition a set
of LEDs from their current color/brightness to a given color/brightness.

### Setup

After installing the extention, add the following to your config file to enable
the `LED_INTERPOLATE` command:

```
[led_interpolate]
```

### Usage

```
LED_INTERPOLATE LED=<config_name> RED=<value> GREEN=<value> BLUE=<value> [WHITE=<value>] [FACTOR=<value>]
```

The command will transition the LED `<config_name>` to the values specified by
`RED`, `GREEN`, `BLUE`, and `WHITE`. `WHITE` is optional and valid only for RGBW
LEDs. If the LEDs are chained, the entire chain will be transitioned. `FACTOR`
can be used to alter the amount by which each step in the transition will change
 the current color.

### Known Issues

* The algorithm is not perfect when it comes to interpolating a chain of LEDs
  which have different starting values. It does its best to get all LEDs in the
  chain to arrive at the desired color at the same time but it's not perfect.
* While the extension manipulates the LEDs Klipper objects directly, bypassing
  any GCode, it may still interfere with normal command processing if the LEDs
  are connected to the MCU controlling the printing operations.

## Idle Timeout
The `idle_timeout` module that Klipper includes can be used to execute GCode
when a predefined number of seconds have elapsed without any activity. When the
time elapses, the printer is put into an "Idle" state.

It would be nice to be able to also execute GCode when the printer comes out of
the "Idle" state. This can be used to turn auxiliary hardware (like the LCD) on
and off. Some users have opted to add such GCode to their `PRINT_START` macros
since it is pretty much the first thing that is executed in normal operations.
I, however, wanted to have the functionality somewhat more integrated into
Klipper in order to be able to catch activity that does not trigger
`PRINT_START`. For example, using the frontend interfaces, the printer can be
brought out of the "Idle" state by a number of actions.

While at it, I also modified the `idle_timeout` modules to not only allow for
execution of GCode when the
printer comes out of "Idle" state but also when the printer is first started.

### Installation
1. Copy _idle_timeout.py_ over the existing file in _klipper/klippy/extras_.
2. Copy _display/menu_keys.py_ ove the existing file in
_klipper/klippy/extras/display_.
3. Restart Klipper.

### Setup
```gcode
[idle_timeout]
#startup_gcode:
#   A list of G-Code commands to execute when Klipper enters "ready"
#   state, which happens on initial startup. These commands will be
#   executed only once.
#ready_gcode:
#    A list of G-Code commands to execute when the printer exits the
#    the "Idle" state.
#idle_gcode:
#   A list of G-Code commands to execute on an idle timeout. See
#   docs/Command_Templates.md for G-Code format. The default is to run
#   "TURN_OFF_HEATERS" and "M84".
#timeout: 600
#   Idle time (in seconds) to wait before running the above G-Code
#   commands. The default is 600 seconds.
```

### Known Issues
Due to the following to aspects of Klipper's implementation:

1. The `idle_timeout` module detects the printer exiting the idle state
   using an event sent from the GCode state. The notification is sent after
   a print GCode command is triggered.
2. Klipper executes macros atomically.

it is possible for the `ready_gcode` to be executed much later after the
printer comes out of the Idle state. This normally happens when the event
that caused the printer to come out of the Idle state is part of a long
macro (like `PRINT_START`). In that case the `ready_gcode` will not
execute until that macro is done.

## probe.py

> **I am not the author of this change. The extension was modified by
> VintageGriffin on Voron's Discord and copied it here so I don't lose
> it. The text below is for documentation purposes only. I do not take or
> accept credit for this extension.**

For some reason, the first probe sample on many Voron printers (may be, others
too) is often off. At this time, the reason for this has not been diagnosed.

However, in order to avoid such a sample from throwing off probe measurements,
this extension has been modified to optionally discard the first sample.

### Installation
1. Replace `klipper/klippy/extras/probe.py` with this file.
2. Restart Klipper.

### Usage
```gcode
[probe]
pin:
#   Probe detection pin. If the pin is on a different microcontroller
#   than the Z steppers then it enables "multi-mcu homing". This
#   parameter must be provided.
#deactivate_on_each_sample: True
#   This determines if Klipper should execute deactivation gcode
#   between each probe attempt when performing a multiple probe
#   sequence. The default is True.
#x_offset: 0.0
#   The distance (in mm) between the probe and the nozzle along the
#   x-axis. The default is 0.
#y_offset: 0.0
#   The distance (in mm) between the probe and the nozzle along the
#   y-axis. The default is 0.
z_offset:
#   The distance (in mm) between the bed and the nozzle when the probe
#   triggers. This parameter must be provided.
#speed: 5.0
#   Speed (in mm/s) of the Z axis when probing. The default is 5mm/s.
#samples: 1
#   The number of times to probe each point. The probed z-values will
#   be averaged. The default is to probe 1 time.
#sample_retract_dist: 2.0
#   The distance (in mm) to lift the toolhead between each sample (if
#   sampling more than once). The default is 2mm.
#lift_speed:
#   Speed (in mm/s) of the Z axis when lifting the probe between
#   samples. The default is to use the same value as the 'speed'
#   parameter.
#samples_result: average
#   The calculation method when sampling more than once - either
#   "median" or "average". The default is average.
#samples_tolerance: 0.100
#   The maximum Z distance (in mm) that a sample may differ from other
#   samples. If this tolerance is exceeded then either an error is
#   reported or the attempt is restarted (see
#   samples_tolerance_retries). The default is 0.100mm.
#samples_tolerance_retries: 0
#   The number of times to retry if a sample is found that exceeds
#   samples_tolerance. On a retry, all current samples are discarded
#   and the probe attempt is restarted. If a valid set of samples are
#   not obtained in the given number of retries then an error is
#   reported. The default is zero which causes an error to be reported
#   on the first sample that exceeds samples_tolerance.
#activate_gcode:
#   A list of G-Code commands to execute prior to each probe attempt.
#   See docs/Command_Templates.md for G-Code format. This may be
#   useful if the probe needs to be activated in some way. Do not
#   issue any commands here that move the toolhead (eg, G1). The
#   default is to not run any special G-Code commands on activation.
#deactivate_gcode:
#   A list of G-Code commands to execute after each probe attempt
#   completes. See docs/Command_Templates.md for G-Code format. Do not
#   issue any commands here that move the toolhead. The default is to
#   not run any special G-Code commands on deactivation.
#discard_first:
#   Boolean value (True or False). When set to "True", the first sample taken
#   will be ignored. Default is False.
```

### Known Issues
This replaces the standard `probe.py` that is part of the Klipper source.
Replacing a standard file will cause the Klipper repository to become dirty,
which will prevent updates from frontends like Mainsail and Fluidd.

Users will have to perform a hard reset of the repository before being able to
update Klipper. After the update, the modified extension will have to
reinstalled manually.

This can potentially cause issue if the `probe.py` file that is included with
Klipper has changed. Replacing the file with this custom version will remove
any changes made by Klipper.
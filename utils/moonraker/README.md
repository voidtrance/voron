# moonraker.py

_moonraker.py_ is a very simple Python module that wraps some of the Moonraker HTTP
APIs as a module.

Currently, it supports querying printer objects and endstops, executing arbitrary
GCode, and emergency stop.

## Usage
```python
import moonraker

printer = moonraker.Connection("my-printer-address")
toolhead = printer.query_object("toolhead")
if "xyz" != toolhead.homed_axes:
    printer.exec_gcode("G28")
```

## Documentation

For module and class documentation, take a look at [moonraker module](__init__.py).
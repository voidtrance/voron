# probe_test.py
_probe_test.py_ is a small Python script that is meant to test the dock
location settings for Klicky probe. It does this by running tests that dock
and undock the probe, repeatedly, checking the status of the probe.

The script works by using the Moonraker Client API. For this, there is a
small Python module `moonraker` that wraps some of the Moonraker APIs in
a Python object.

## Running the script
```
usage: probe_test.py [-h] [-i ITERATIONS] [-m MOVES] [--min-move-speed MIN_MOVE_SPEED]
                     [--max-move-speed MAX_MOVE_SPEED]
                     printer

Run a Klicky probe attach/dock test by moving the tool head to random locations and then
attempting to dock/undock the probe.

positional arguments:
  printer               Network name of the printer

options:
  -h, --help            show this help message and exit
  -i ITERATIONS, --iterations ITERATIONS
                        Number of test iterations. (default: 10)
  -m MOVES, --moves MOVES
                        Number of toolhead moves per iteration. (default: 4)
  --min-move-speed MIN_MOVE_SPEED
                        Minimum movement speed (mm/min). (default: 300)
  --max-move-speed MAX_MOVE_SPEED
                        Maximum movement speed (mm/min). (default: 20000)
```
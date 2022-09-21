#!/usr/bin/env python3
#
# Copyright 2022 Mitko Haralanov <voidtrance@gmail.com>
#
# Perform some dock/undock tests for Klicky probe.
# This is meant to test that the alignment and position
# settings have been configured correctly as to make the
# dock reliable.
import sys
import enum
import random
import moonraker
import argparse

parser = argparse.ArgumentParser(
    description="""Run a Klicky probe attach/dock test by
    moving the tool head to random locations and then
    attempting to dock/undock the probe.""",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--iterations", type=int, default=10,
                    help="Number of test iterations.")
parser.add_argument("-m", "--moves", type=int, default=4,
                    help="Number of toolhead moves per iteration.")
parser.add_argument("--min-move-speed", type=int, default=300,
                    help="Minimum movement speed (mm/min).")
parser.add_argument("--max-move-speed", type=int, default=20000,
                    help="Maximum movement speed (mm/min).")
parser.add_argument("--no-qgl", action="store_true",
                    help="""Don't do Quad Gantry Leveling
                     before running tests.""")
parser.add_argument("printer", default="localhost",
                    help="Network name of the printer")


class Axis(enum.IntEnum):
    X = 0
    Y = 1
    Z = 2


class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class AxisLimits:
    def __init__(self, min, max):
        self.min = min
        self.max = max


class PrinterAxes:
    def __init__(self):
        self.x = AxisLimits(0, 0)
        self.y = AxisLimits(0, 0)
        self.z = AxisLimits(0, 0)


class ProbeState(enum.IntEnum):
    OPEN = 0
    TRIGGERED = 1


def get_random_point(axes, margin=50):
    x = random.randrange(axes.x.min + margin, axes.x.max - margin)
    y = random.randrange(axes.y.min + margin, axes.y.max - margin)
    z = random.randrange(axes.z.min + 2, axes.z.max)
    return Point(x, y, z)


def get_probe_state(printer):
    printer.exec_gcode("QUERY_PROBE")
    status = printer.query_object("probe", ["last_query"])
    return ProbeState(status["last_query"])


def do_test_moves(printer, axes, num, min_speed, max_speed):
    for move in range(num):
        move_speed = random.randrange(min_speed, max_speed)
        where = get_random_point(axes)
        if not printer.exec_gcode(f"G0 X{where.x} Y{where.y} F{move_speed}"):
            return False
    return True


def test_dock_undock(printer, axes, opts):
    for iteration in range(opts.iterations):
        print(f"{iteration+1}", end=" ", flush=True)
        if not do_test_moves(printer, axes, opts.moves,
                             opts.min_move_speed, opts.max_move_speed):
            return False
        if not printer.exec_gcode("ATTACH_PROBE"):
            return False
        probe_state = get_probe_state(printer)
        if probe_state != ProbeState.OPEN:
            return False
        if not printer.exec_gcode("DOCK_PROBE"):
            return False
        probe_state = get_probe_state(printer)
        if probe_state != ProbeState.TRIGGERED:
            return False
    return True


def test_dock_move_undock(printer, axes, opts):
    for iteration in range(opts.iterations):
        print(f"{iteration+1}", end=" ", flush=True)
        if not do_test_moves(printer, axes, opts.moves,
                             opts.min_move_speed, opts.max_move_speed):
            return False
        if not printer.exec_gcode("ATTACH_PROBE"):
            return False
        probe_state = get_probe_state(printer)
        if probe_state != ProbeState.OPEN:
            return False
        if not do_test_moves(printer, axes, opts.moves,
                             opts.min_move_speed, opts.max_move_speed):
            return False
        if not printer.exec_gcode("DOCK_PROBE"):
            return False
        probe_state = get_probe_state(printer)
        if probe_state != ProbeState.TRIGGERED:
            return False
    return True


def main():
    random.seed()
    opts = parser.parse_args()

    printer = moonraker.Connection(opts.printer)
    toolhead = printer.query_object("toolhead")
    printer_axes = PrinterAxes()
    printer_axes.x.min = int(toolhead["axis_minimum"][Axis.X])
    printer_axes.x.max = int(toolhead["axis_maximum"][Axis.X])
    printer_axes.y.min = int(toolhead["axis_minimum"][Axis.Y])
    printer_axes.y.max = int(toolhead["axis_maximum"][Axis.Y])
    printer_axes.z.min = int(toolhead["axis_minimum"][Axis.Z])
    printer_axes.z.max = int(toolhead["axis_maximum"][Axis.Z])

    # First, home the printer.
    if toolhead["homed_axes"] != "xyz":
        print("Homing printer...", end=" ", flush=True)
        if not printer.exec_gcode("G28"):
            print("Failed to home printer.")
            return 1
        print("done.")

    if not opts.no_gql:
        # Level the printer if not leveled
        leveled = printer.query_object("quad_gantry_level", ["applied"])
        if not leveled["applied"]:
            print("Leveling printer...", end=" ", flush=True)
            if not printer.exec_gcode("QUAD_GANTRY_LEVEL"):
                print("Failed to level printer.")
                return 1
            print("done.")
    else:
        print("Skipping gantry leveling!", file=sys.stderr)
        print("WARNING: In extreme cases, this may cause issues!", file=sys.stderr)

    # Now, run tests...
    print("Running Dock/Undock test...", end=" ", flush=True)
    status = test_dock_undock(printer, printer_axes, opts)
    if not status:
        print("failed.")
        return 1
    print("done.")

    print("Running Dock/Move/Undock test...", end=" ")
    status = test_dock_move_undock(printer, printer_axes, opts)
    if not status:
        print("failed.")
        return 1
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

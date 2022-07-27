#!/usr/bin/env python3
#
# Generate parameters for an adaptive bed mesh
#
# Copyright (C) 2022  Mitko Haralanov <voidtrance@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import os
import re
import sys
import math
import argparse
import tempfile

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_MESH = 2

try:
    from preprocess_cancellation import preprocessor
except ImportError:
    #sys.stderr.write("Failed to import preprocess_cancellation\n")
    # sys.exit(EXIT_ERROR)
    pass


arg_parser = argparse.ArgumentParser(description="""Generate parameters for
an adaptive bed mesh. This tool will parse the input GCode file to
generate a list of printed objects and the are of the bed each
object takes up. It will then output a set of values that can be
passed to Klipper's BED_MESH_CALIBRATE command. With these values
Klipper will be instructed to measure only the area of the print
bed that will be used by the objects in the GCode file.""")
arg_parser.add_argument("file", type=str, help="GCode filename")
arg_parser.add_argument("--mesh_min", type=str, default="0,0",
                        help="Minimum mesh coordinates (X,Y)")
arg_parser.add_argument("--mesh_max", type=str, default="0,0",
                        help="Maximum mesh coordinates (X,Y)")
arg_parser.add_argument("--probes", type=str, default="0,0",
                        help="Number of probe points (X,Y)")
arg_parser.add_argument("--size", type=str, required=True,
                        help="Printer bed size")
arg_parser.add_argument("--margin", type=float, default=5.0,
                        help="Margin (in mm) to add to print area")
arg_parser.add_argument("--cutoff", type=int, default=10,
                        help="""Area of bed (in percent) that will
                                serve as a cutoff. If the print area
                                is smaller, no bedmesh will be done.""")


OBJECT_REG = re.compile(
    r'^EXCLUDE_OBJECT_DEFINE NAME=(?P<name>[^ ]+) CENTER=(?P<center>[0-9,.]+) POLYGON=(?P<polygon>[]0-9,.[]+)$')


class Point:
    def __init__(self, x, y):
        self.x = round(x, 5)
        self.y = round(y, 5)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Point({self.x},{self.y})"


class PrintObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_printed_objects(gcode_file):
    printed_objects = []

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        # First, pass the GCode file through the cancellation
        # processor, which will identify all of the objects and
        # annotate with their area.
        gcode_file = os.path.abspath(os.path.expanduser(gcode_file))
        tmp_file = os.path.join(tmp_dir_name, os.path.basename(gcode_file))
        with open(gcode_file, 'r') as ifd:
            with open(tmp_file, 'w') as ofd:
                try:
                    preprocessor(ifd, ofd)
                except:
                    return printed_objects

        # Next, we go through the processed file extracting all
        # of the object definitions.
        with open(tmp_file, 'r') as fd:
            for line in fd:
                if line.startswith("EXCLUDE_OBJECT_DEFINE"):
                    obj = OBJECT_REG.match(line)
                    center = eval("(" + obj.group("center") + ")")
                    polygon = eval(obj.group("polygon"))
                    box = []
                    for coord in polygon:
                        box.append(Point(coord[0], coord[1]))
                    printed = PrintObject(name=obj.group("name"),
                                          center=Point(*center),
                                          box=box)
                    printed_objects.append(printed)

        os.unlink(tmp_file)

    return printed_objects


def get_print_area(objects, size, margin):
    min_x, min_y = 99999, 99999
    max_x, max_y = 0, 0
    for obj in objects:
        min_x = min(min_x, obj.box[0].x)
        min_y = min(min_y, obj.box[0].y)
        max_x = max(max_x, obj.box[2].x)
        max_y = max(max_y, obj.box[2].y)

    min_x = max(0, min_x - margin)
    max_x = min(size.x, max_x + margin)
    min_y = max(0, min_y - margin)
    max_y = min(size.y, max_y + margin)
    return [Point(min_x, min_y), Point(min_x, max_y), Point(max_x, max_y), Point(max_x, min_y)]


def get_bed_mesh_area(area, mesh_min, mesh_max):
    min_x = max(area[0].x, mesh_min.x)
    max_x = min(area[2].x, mesh_max.x)
    min_y = max(area[0].y, mesh_min.y)
    max_y = min(area[2].y, mesh_max.y)
    return [Point(min_x, min_y), Point(min_x, max_y), Point(max_x, max_y), Point(max_x, min_y)]


def output_bed_mesh_params(mesh_min, mesh_max, probes, ref_index):
    print(f"VALUE_UPDATE:min_mesh={mesh_min.x},{mesh_min.y}")
    print(f"VALUE_UPDATE:max_mesh={mesh_max.x},{mesh_max.y}")
    print(f"VALUE_UPDATE:probe_count={probes[0]},{probes[1]}")
    print(f"VALUE_UPDATE:ref_index={ref_index}")


def parse_params(options):
    for attr in ("size", "mesh_min", "mesh_max"):
        value = getattr(options, attr)
        setattr(options, attr, tuple([float(x)
                                      for x in value.split(",")]))
    options.probes = tuple([int(x) for x in options.probes.split(",")])
    for attr in ("size", "mesh_min", "mesh_max"):
        value = getattr(options, attr)
        setattr(options, attr, Point(*value))
    options.cutoff = options.cutoff / 100.0
    return options


def main():
    opts = arg_parser.parse_args(sys.argv[1:])

    opts = parse_params(opts)

    objects = get_printed_objects(opts.file)
    if not objects:
        return EXIT_ERROR

    area = get_print_area(objects, opts.size, opts.margin)
    bed_mesh_area = get_bed_mesh_area(area, opts.mesh_min, opts.mesh_max)

    if bed_mesh_area[0] == opts.mesh_min and bed_mesh_area[2] == opts.mesh_max:
        output_bed_mesh_params(opts.mesh_min, opts.mesh_max, opts.probes,
                               int((opts.probes[0] * opts.probes[1]) / 2))
    else:
        ratio = Point((bed_mesh_area[2].x - bed_mesh_area[0].x) / opts.size.x,
                      (bed_mesh_area[2].y - bed_mesh_area[0].y) / opts.size.y)

        # If the print area used is less than the cutoff, don't need
        # a bedmesh.
        if ratio.x <= opts.cutoff and ratio.y <= opts.cutoff:
            return EXIT_NO_MESH

        # Use a minimum of 3 probe points in each dimension
        probes = (max(3, math.ceil(opts.probes[0] * ratio.x)),
                  max(3, math.ceil(opts.probes[1] * ratio.y)))

        ref_index = int((probes[0] * probes[1]) / 2)
        output_bed_mesh_params(bed_mesh_area[0], bed_mesh_area[2],
                               probes, ref_index)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

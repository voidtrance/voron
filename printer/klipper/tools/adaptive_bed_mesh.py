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
    sys.stderr.write("Failed to import preprocess_cancellation\n")
    sys.exit(EXIT_ERROR)

arg_parser = argparse.ArgumentParser(description="""Generate parameters for
an adaptive bed mesh. This tool will parse the input GCode file to
generate a list of printed objects and the are of the bed each
object takes up. It will then output a set of values that can be
passed to Klipper's BED_MESH_CALIBRATE command. With these values
Klipper will be instructed to measure only the area of the print
bed that will be used by the objects in the GCode file.""",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
arg_parser.add_argument("file", type=str, help="GCode filename")
arg_parser.add_argument("--mesh_min", type=str, default="0,0",
                        help="Minimum mesh coordinates (X,Y)")
arg_parser.add_argument("--mesh_max", type=str, default="0,0",
                        help="Maximum mesh coordinates (X,Y)")
arg_parser.add_argument("--probes", type=str, default="0,0",
                        help="Number of probe points (X,Y)")
arg_parser.add_argument("--size", type=str, required=True,
                        help="Printer bed size (X,Y)")
arg_parser.add_argument("--margin", type=float, default=5.0,
                        help="Margin (in mm) to add to print area")
arg_parser.add_argument("--cutoff", type=int, default=10,
                        help="""Area of bed (in percent) that will
                                serve as a cutoff. If the print area
                                is smaller, no bed meshing will be
                                done.""")
arg_parser.add_argument("--algo", type=str, default="lagrange",
                        choices=["lagrange", "bicubic"],
                        help="Bed mesh interpolation algorithm.")
arg_parser.add_argument("--use-spacing", type=int, const=0, nargs="?",
                        default=None,
                        help="""Generate X and Y probe point counts
                                based on the spacing between the
                                probe points in the default mesh.
                                A ratio between the spacing in the
                                adaptive bed mesh and the default bed
                                mesh is computed and probe points are
                                re-computed based on that ratio. If a
                                non-zero value is given, ratio lower
                                that that percentage will be ignored.""")

OBJECT_REG = re.compile(
    r'^EXCLUDE_OBJECT_DEFINE NAME=(?P<name>[^ ]+) CENTER=(?P<center>[0-9,.]+) POLYGON=(?P<polygon>[]0-9,.[]+)$')


class Point:
    def __init__(self, x, y):
        self.x = round(x, 5)
        self.y = round(y, 5)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x},{self.y})"


class PrintObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_printed_objects(gcode_file):
    object_data = []
    printed_objects = []

    # Detect if the file has already been processed and if so, use
    # that information.
    with open(gcode_file, 'r') as ifd:
        for line in ifd:
            if line.startswith("EXCLUDE_OBJECT_DEFINE"):
                object_data.append(line)

    if not object_data:
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
                        object_data.append(line)

            os.unlink(tmp_file)

    for object_def in object_data:
        obj = OBJECT_REG.match(object_def)
        center = eval("(" + obj.group("center") + ")")
        polygon = eval(obj.group("polygon"))
        box = []
        for coord in polygon:
            box.append(Point(coord[0], coord[1]))
        printed = PrintObject(name=obj.group("name"),
                              center=Point(*center),
                              box=box)
        printed_objects.append(printed)
    return printed_objects


def get_print_area(objects, size, margin):
    min_x, min_y = 99999, 99999
    max_x, max_y = 0, 0
    for obj in objects:
        min_x = min([min_x] + [p.x for p in obj.box])
        min_y = min([min_y] + [p.y for p in obj.box])
        max_x = max([max_x] + [p.x for p in obj.box])
        max_y = max([max_y] + [p.y for p in obj.box])

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


def output_bed_mesh_params(mesh_min, mesh_max, probes, algorithm):
    print(f"VALUE_UPDATE:min_mesh={mesh_min.x},{mesh_min.y}")
    print(f"VALUE_UPDATE:max_mesh={mesh_max.x},{mesh_max.y}")
    print(f"VALUE_UPDATE:probe_count={probes.x},{probes.y}")
    print(f"VALUE_UPDATE:algorithm={algorithm}")


def parse_params(options):
    for attr in ("size", "mesh_min", "mesh_max"):
        value = getattr(options, attr)
        setattr(options, attr, tuple([float(x)
                                      for x in value.split(",")]))
    options.probes = Point(*[int(x) for x in options.probes.split(",")])
    for attr in ("size", "mesh_min", "mesh_max"):
        value = getattr(options, attr)
        setattr(options, attr, Point(*value))
    options.cutoff = options.cutoff / 100.0
    if options.use_spacing is not None:
        if options.use_spacing != 0:
            options.use_spacing = options.use_spacing / 100.0
    return options


def main():
    opts = arg_parser.parse_args(sys.argv[1:])
    opts = parse_params(opts)

    if not opts.file or not os.access(opts.file, os.R_OK):
        print(f"Cannot read GCode file '{opts.file}", file=sys.stderr)
        return EXIT_ERROR

    objects = get_printed_objects(opts.file)
    if not objects:
        print(f"Did not find any objects in GCode file '{opts.file}",
              file=sys.stderr)
        return EXIT_ERROR

    area = get_print_area(objects, opts.size, opts.margin)
    default_bed_mesh_size = Point(opts.mesh_max.x - opts.mesh_min.x,
                                  opts.mesh_max.y - opts.mesh_min.y)
    bed_mesh_area = get_bed_mesh_area(area, opts.mesh_min, opts.mesh_max)
    bed_mesh_size = Point(bed_mesh_area[2].x - bed_mesh_area[0].x,
                          bed_mesh_area[2].y - bed_mesh_area[0].y)

    if bed_mesh_area[0] == opts.mesh_min and bed_mesh_area[2] == opts.mesh_max:
        output_bed_mesh_params(opts.mesh_min, opts.mesh_max, opts.probes,
                               opts.algo)
        return EXIT_SUCCESS

    ratio = Point(bed_mesh_size.x / opts.size.x,
                  bed_mesh_size.y / opts.size.y)

    # If the print area used is less than the cutoff, don't need
    # a bedmesh.
    if opts.cutoff and ratio.x <= opts.cutoff and ratio.y <= opts.cutoff:
        return EXIT_NO_MESH

    # Compute the number of probes to be used based on print
    # area ratio and min/max probe counts for each algorithm.
    probes = Point(math.ceil(opts.probes.x * ratio.x),
                   math.ceil(opts.probes.y * ratio.y))

    # If any of the axis ends up having less than 3 points, the mesh is
    # not very useful so ensure that both axes have at least 3 probe
    # points.
    if min(probes.x, probes.y) < 3:
        probes.x = max(probes.x, 3)
        probes.y = max(probes.y, 3)

    if opts.use_spacing is not None:
        # By definition, the number of probe points will be less than the
        # number defined in the configuration.
        # When computing the number of points, some fidelity can be lost
        # due to the fact that probe points have to be integers. This can
        # result in there being too much distance between the probe points.
        default_spacing = Point(default_bed_mesh_size.x / opts.probes.x,
                                default_bed_mesh_size.y / opts.probes.y)
        spacing = Point(bed_mesh_size.x / probes.x, bed_mesh_size.y / probes.y)
        spacing_delta = Point((spacing.x - default_spacing.x) / spacing.x,
                              (spacing.y - default_spacing.y) / spacing.y)
        if spacing_delta.x > 0.0 and spacing_delta.x >= opts.use_spacing:
            probes.x += math.ceil(probes.x * spacing_delta.x)
        if spacing_delta.y > 0.0 and spacing_delta.y >= opts.use_spacing:
            probes.y += math.ceil(probes.y * spacing_delta.y)

    # Ensure that both axes have an odd number of probe points.
    probes.x += 1 - (probes.x % 2)
    probes.y += 1 - (probes.y % 2)

    # Determine the correct interpolation algorithm.
    # For more information on this, see
    # https://www.klipper3d.org/Bed_Mesh.html#mesh-interpolationcd
    algo = opts.algo
    probe_count_limits = {"lagrange": (0, 6), "bicubic": (4, 9999)}
    if min(probes.x, probes.y) < probe_count_limits[algo][0] or \
            max(probes.x, probes.y) > probe_count_limits[algo][1]:
        idx = list(probe_count_limits.keys()).index(algo)
        algo = list(probe_count_limits.keys())[1 - idx]

    output_bed_mesh_params(bed_mesh_area[0], bed_mesh_area[2], probes,
                           algo)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())

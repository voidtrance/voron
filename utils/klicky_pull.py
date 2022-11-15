#!/usr/bin/env python3
import sys
import re
import os
import subprocess
import tempfile
import shutil
import difflib

VAR_REPLACE = ["_User_Variables", "_Probe_Variables"]
FILE_SPECIFIC = {
    "klicky-variables.cfg": [
        (r'^(variable_max_bed_y:\s*)[0-9]+(.*)$', r'\g<1>300\2'),
        (r'^(variable_max_bed_x:\s*)[0-9]+(.*)$', r'\g<1>300\2'),
        (r'^(variable_z_endstop_x:\s*)[0-9]+(.*)$', r'\g<1>206\2'),
        (r'^(variable_z_endstop_y:\s*)[0-9]+(.*)$', r'\g<1>305\2'),
        (r'^(variable_docklocation_x:\s*)[0-9]+(.*)$', r'\g<1>0\2'),
        (r'^(variable_docklocation_y:\s*)[0-9]+(.*)$', r'\g<1>307\2'),
        (r'^(Variable_dockmove_x:\s*)[0-9]+(.*)$', r'\g<1>40\2'),
        (r'^(Variable_attachmove_x:\s*)[0-9]+(.*)$', r'\g<1>0\2'),
        (r'^(Variable_attachmove_y:\s*)[0-9]+(.*)$', r'\g<1>30\2'),
    ],
    "klicky-probe.cfg": [
        (r'^#\[include ./klicky-specific.cfg\](.*)$',
         r'[include ./klicky-specific.cfg]\1'),
        (r'^#\[include ./klicky-bed-mesh-calibrate.cfg\](.*)$',
         r'[include ./klicky-bed-mesh-calibrate.cfg]\1'),
        (r'^#\[include ./klicky-quad-gantry-level.cfg\](.*)$',
         r'[include ./klicky-quad-gantry-level.cfg]\1')
    ]
}


def get_git_top():
    cdup = subprocess.getoutput("git rev-parse --show-cdup")
    return os.path.abspath(os.path.join(os.getcwd(), cdup))


def replace_vars(fileset, tmpdir):
    out_fileset = []
    for filename in fileset:
        with open(filename, 'r') as fd:
            content = fd.readlines()
        for string in VAR_REPLACE:
            out_content = []
            for line in content:
                out_content.append(re.sub(string, "_Klicky" + string, line))
            content = out_content[:]
        out_filename = os.path.join(tmpdir, os.path.basename(filename))
        with open(out_filename, 'w') as fd:
            for line in content:
                fd.write(line)
        out_fileset.append(out_filename)
    return out_fileset


def replace_file_specific(fileset):
    for filename in fileset:
        string_sets = FILE_SPECIFIC.get(os.path.basename(filename), None)
        if not string_sets:
            continue
        with open(filename, 'r') as fd:
            content = fd.readlines()
        for string_set in string_sets:
            out_content = []
            for line in content:
                out_content.append(re.sub(string_set[0], string_set[1], line))
            content = out_content[:]

        with open(filename, 'w') as fd:
            for line in content:
                fd.write(line)


def find_diffs(fileset, local_dir):
    differ = difflib.Differ()
    different = []
    for filename in fileset:
        local_filename = os.path.join(local_dir, os.path.basename(filename))
        with open(filename, 'r') as fd:
            text1 = fd.readlines()
        with open(local_filename, 'r') as fd:
            text2 = fd.readlines()
        diff = list(differ.compare(text1, text2))
        for line in diff:
            if line.startswith(("-", "+", "?")):
                print(filename, line, end="")
                if filename not in different:
                    different.append(filename)
    return different


def main():
    git_top = get_git_top()
    klicky_repo = os.path.abspath(os.path.join(git_top, "..", "Klicky-Probe"))
    local_macro_dir = os.path.join(
        git_top, "printer", "config", "macros", "klicky")
    remote_macro_dir = os.path.join(klicky_repo, "Klipper_macros")
    tmpdir = tempfile.mkdtemp(prefix=".klicky_pull.")

    remote_fileset = []
    for filename in os.listdir(local_macro_dir):
        remote_filename = os.path.join(remote_macro_dir, filename)
        if os.path.exists(remote_filename):
            remote_fileset.append(remote_filename)

    fileset = replace_vars(remote_fileset, tmpdir)
    replace_file_specific(fileset)
    diff_fileset = find_diffs(fileset, local_macro_dir)

    for filename in diff_fileset:
        shutil.copy(filename, os.path.join(local_macro_dir,
                                           os.path.basename(filename)))

    shutil.rmtree(tmpdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

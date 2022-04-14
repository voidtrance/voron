# Run a shell command via gcode
#
# Copyright (C) 2019  Eric Callahan <arksine.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import os
import shlex
import subprocess
import logging


class ShellCommand:
    def __init__(self, config):
        self.name = config.get_name().split()[-1]
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        cmd = config.get('command')
        cmd = os.path.expanduser(cmd)
        self.command = shlex.split(cmd)
        self.timeout = config.getfloat('timeout', 2., above=0.)
        self.verbose = config.getboolean('verbose', True)
        self.on_success = config.get('success', None)
        self.on_failure = config.get('failure', None)
        self.proc_fd = None
        self.partial_output = ""
        self.gcode.register_mux_command(
            "RUN_SHELL_COMMAND", "CMD", self.name,
            self.cmd_RUN_SHELL_COMMAND,
            desc=self.cmd_RUN_SHELL_COMMAND_help)

    def _process_output(self, eventime):
        if self.proc_fd is None:
            return
        try:
            data = os.read(self.proc_fd, 4096)
        except Exception:
            pass
        data = self.partial_output + data.decode()
        if '\n' not in data:
            self.partial_output = data
            return
        elif data[-1] != '\n':
            split = data.rfind('\n') + 1
            self.partial_output = data[split:]
            data = data[:split]
        else:
            self.partial_output = ""
        self.gcode.respond_info(data)

    cmd_RUN_SHELL_COMMAND_help = "Run a linux shell command"

    def cmd_RUN_SHELL_COMMAND(self, params):
        gcode_params = params.get('PARAMS', '')
        gcode_params = shlex.split(gcode_params)
        reactor = self.printer.get_reactor()
        try:
            proc = subprocess.Popen(
                self.command + gcode_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            logging.exception(
                "shell_command: Command {%s} failed" % (self.name))
            raise self.gcode.error("Error running command {%s}" % (self.name))
        if self.verbose:
            self.proc_fd = proc.stdout.fileno()
            self.gcode.respond_info("Running Command {%s}...:" % (self.name))
            hdl = reactor.register_fd(self.proc_fd, self._process_output)
        eventtime = reactor.monotonic()
        endtime = eventtime + self.timeout
        complete = False
        while eventtime < endtime:
            eventtime = reactor.pause(eventtime + .05)
            if proc.poll() is not None:
                complete = True
                break
        if not complete:
            proc.terminate()
        status = proc.wait()
        if self.verbose:
            if self.partial_output:
                self.gcode.respond_info(self.partial_output)
                self.partial_output = ""
            reactor.unregister_fd(hdl)
            self.proc_fd = None
        if status == 0 and self.on_success:
            self.gcode.run_script_from_command(self.on_success)
        elif self.on_failure:
            self.gcode.run_script_from_command(self.on_failure)
        if self.verbose:
            if complete:
                msg = "Command {%s} finished\n" % (self.name)
            else:
                msg = "Command {%s} timed out" % (self.name)
            self.gcode.respond_info(msg)


def load_config_prefix(config):
    return ShellCommand(config)

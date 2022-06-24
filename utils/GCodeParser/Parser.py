from . import GCode


class GCodeParser:
    def __init__(self):
        return

    def parse(self, gcode):
        parsed = None
        if gcode.strip() and not gcode.startswith(';'):
            parsed = GCode.GCodeCommand(gcode)
        return parsed

    def parse_file(self, filename):
        with open(filename, 'r') as fd:
            for line in fd:
                yield self.parse(line)

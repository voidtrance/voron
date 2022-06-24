import regex


class GCodeParamParseError(Exception):
    pass


class GCodeParam:
    gcode_param_regexp = regex.compile(r'^(?P<name>[A-Z]+)=?(?P<value>.+)$')
    float_regexp = regex.compile(r'(?P<mantisa>[0-9-]+)(?:\.(?P<exp>[0-9]+))?')

    def __init__(self, param):
        parsed = self.gcode_param_regexp.match(param)
        if not parsed:
            raise GCodeParamParseError

        self.__name = parsed.group("name")
        self.__raw_value = parsed.group("value")
        v_parsed = self.float_regexp.match(self.__raw_value)
        if v_parsed:
            if v_parsed.group("exp"):
                self.__value = (float(self.__raw_value),
                                len(v_parsed.group("exp")))
            elif not v_parsed.group("exp") and self.__raw_value.endswith("."):
                self.__value = (float(self.__raw_value), 0)
            else:
                self.__value = (int(self.__raw_value), 0)
        else:
            self.__value = (self.__raw_value, None)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value[0]

    def __str__(self):
        if self.__value[1] == None:
            v = self.__value
        elif self.__value[1] != 0:
            v = f"{self.__value[0]:{self.__value[1]}f}"
        else:
            v = f"{self.__value[0]}"
        return f"{self.name}{v}"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, GCodeParam):
            return self.name == other.name
        else:
            return False


class GCodeCommandParseError(Exception):
    pass


class GCodeCommand:
    gcode_regexp = regex.compile(
        r'^(?P<cmd>(?P<prefix>[A-Z])(?P<code>[0-9]+))(?:\ (?P<data>[^;]*))?(?:\ *;\ *(?P<comment>.*))?$')
    macro_r = regex.compile(
        r'^(?P<cmd>[^\ ]+)\ *(?P<data>[^;]*)(?:;\ *(?P<comment>.*))?$')

    def __init__(self, command):
        self.__is_macro = False
        parsed = self.gcode_regexp.match(command)
        if not parsed:
            parsed = self.macro_r.match(command)
            if not parsed:
                raise GCodeCommandParseError
            self.__is_macro = True
        self.__cmd = parsed.group("cmd")
        self.__raw_params = parsed.group("data")
        self.__comment = parsed.group("comment")
        self.__cmd_class = parsed.group("prefix") \
            if not self.__is_macro else None
        self.__cmd_code = int(parsed.group("code")) \
            if not self.__is_macro else 0
        self.__params = []

        if self.__raw_params:
            for param in self.__raw_params.split():
                self.__params.append(GCodeParam(param))

    @property
    def command(self):
        return self.__cmd

    @property
    def command_class(self):
        return self.__class

    @property
    def command_code(self):
        return self.__cmd_code

    @property
    def comment(self):
        return self.__comment

    @property
    def macro(self):
        return self.__is_macro

    def has_param(self, name):
        return name in self.__params

    def get_param(self, name):
        for param in self.__params:
            if param == name:
                return param
        return None

    def get_params(self):
        for param in self.__params:
            yield(param)

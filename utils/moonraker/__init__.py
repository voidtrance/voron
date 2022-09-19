from . import requests

DEFAULT_MOONRAKER_ADDRESS = "localhost"
DEFAULT_MOONRAKER_PORT = 7125


class Connection:
    """
    A class representing a connection to a Moonraker instance.
    The class provides methods for querying printer objects and
    executing GCode.

    Methods
    -------
    get_objects():
        Get a list of all defined printer objects.
    query_object(object, properties=[]):
        Query a printer object and return object attributes.
    emergency_stop():
        Execute an emergency stop on the printer.
    query_endstops(endstop=None):
        Return the state of endstops.
    exec_gcode(gcode):
        Execute GCode command(s).
    """

    def __init__(self, moonraker_address: str = DEFAULT_MOONRAKER_ADDRESS,
                 moonraker_port: int = DEFAULT_MOONRAKER_PORT):
        """
        Class constructor.

        Parameters
        ----------
            moonraker_address : str, optional
                Network address of the Moonraker service. Default is
                DEFAULT_MOONRALER_ADDRESS.
            moonraker_port : int, optional
                Network port of the Moonraker service. Default is
                DEFAULT_MOONRALER_PORT.
        """
        self.address = f"http://{moonraker_address}:{moonraker_port}"
        self.printer_objects = self.get_objects()
        self.config = self.query_object("configfile", ["config"])

    def get_objects(self) -> list:
        """
        Return a list of all defined printer objects.

        Parameters
        ----------
            None

        Returns
        -------
            List of objects.
        """
        request = requests.Request(self.address, "printer/objects/list")
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS:
            return response.data["objects"]
        return []

    def query_object(self, object: str, properties: str | list | dict = []) -> dict:
        """
        Query a printer object and return a dictionary of object attributes.

        Parameters
        ----------
            object : str
                Object to query.
            properties : str | list | dict, optional
                Name, list of names, or a dictionary of object attributes
                which to query. If not specified, all object attributes
                will be queried.

        Returns
        -------
            A dictionary of object attributes.
        """
        if object not in self.printer_objects:
            return None
        if isinstance(properties, str):
            properties = [properties]
        request = requests.Request(self.address, "printer/objects/query")
        request.add_params({object: properties})
        response = request.get()
        if response.status == requests.ResponseType.ERROR:
            return None
        return response.data["status"][object]

    def emergency_stop(self) -> bool:
        """
        Execute an emergency stop on the printer.

        Parameters
        ----------
            None

        Returns
        -------
            True if stop executed successfully.
            False, otherwise.
        """
        request = requests.Request(self.address, "printer/emergency_stop")
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS:
            return True
        return False

    def query_endstops(self, endstop: str | list = None) -> dict:
        """
        Query printer endstop(s) state(s).

        Parameters
        ----------
            endstop : str | list, optional
                Name or list of names of endstops to query.

        Returns
        -------
            A dictionary of endstop states.
        """
        request = requests.Request(
            self.address, "printer/query_endstops/status")
        response = request.get()
        if response.status == requests.ResponseType.ERROR:
            return {}
        if not endstop:
            return response.data
        if isinstance(endstop, str):
            return response.data.get(endstop, None)
        return {x: response.data[x] for x in endstop}

    def exec_gcode(self, gcode: str) -> bool:
        """
        Execute GCode command(s) on the printer.

        Parameters
        ----------
            gcode : str
                A string containing GCode command(s)

        Returns
        -------
            True if command(s) executed successfully.
            False, otherwise.
        """
        request = requests.Request(self.address, "printer/gcode/script",
                                   requests.RequestType.POST)
        request.add_params({"script": [gcode]})
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS and \
                response.data == "ok":
            return True
        return False

    def firmware_restart(self) -> bool:
        """
        Restart the printer's MCU firmware.

        Parameters
        ----------
            None

        Returns
        -------
            True if restart succeeded. False, otherwise.
        """
        request = requests.Request(self.address, "printer/firmware_restart",
                                   requests.RequestType.POST)
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS and \
                response.data == "ok":
            return True
        return False

    def host_restart(self) -> bool:
        """
        Restart host software.

        Parameters
        ----------
            None

        Returns
        -------
            True on success. False, otherwise.
        """
        request = requests.Request(self.address, "printer/restart",
                                   requests.RequestType.POST)
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS and \
                response.data == "ok":
            return True
        return False

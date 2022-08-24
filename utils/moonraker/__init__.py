from . import requests

DEFAULT_MOONRAKER_ADDRESS = "localhost"
DEFAULT_MOONRAKER_PORT = 7125


class Connection:
    def __init__(self, moonraker_address=DEFAULT_MOONRAKER_ADDRESS,
                 moonraker_port=DEFAULT_MOONRAKER_PORT):
        self.address = f"http://{moonraker_address}:{moonraker_port}"
        self.printer_objects = self.get_objects()
        self.config = self.query_object("configfile", ["config"])

    def get_objects(self):
        request = requests.Request(self.address, "printer/objects/list")
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS:
            return response.data["objects"]
        return []

    def query_object(self, object, properties=[]):
        if object not in self.printer_objects:
            return None
        request = requests.Request(self.address, "printer/objects/query")
        request.add_params({object: properties})
        response = request.get()
        if response.status == requests.ResponseType.ERROR:
            return None
        return response.data["status"][object]

    def emergency_stop(self):
        request = requests.Request(self.address, "printer/emergency_stop")
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS:
            return True
        return False

    def query_endstops(self, endstop=None):
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

    def exec_gcode(self, gcode):
        request = requests.Request(self.address, "printer/gcode/script",
                                   requests.RequestType.POST)
        request.add_params({"script": [gcode]})
        response = request.get()
        if response.status == requests.ResponseType.SUCCESS and \
                response.data == "ok":
            return True
        return False

import urllib.parse
import urllib.request
import json
import enum


@enum.unique
class RequestType(enum.IntEnum):
    GET = enum.auto()
    POST = enum.auto()


@enum.unique
class ResponseType(enum.IntEnum):
    SUCCESS = enum.auto()
    ERROR = enum.auto()


class Response:
    def __init__(self, status: int, data: str):
        self.status = status
        self.reason = None
        self.data = None
        if self.status == ResponseType.SUCCESS:
            data = json.loads(data)
            self.data = data["result"]
        else:
            self.reason = data


class Request:
    def __init__(self, server: str, url: str, method: RequestType = RequestType.GET):
        self.server = server
        self.url = url
        self.method = method
        self.data = {}
        self.params = []

    def add_params(self, params: str | list | dict):
        if isinstance(params, dict):
            for key, value in params.items():
                if not value:
                    self.params.append(urllib.parse.quote_plus(key))
                else:
                    properties = [urllib.parse.quote_plus(x)
                                  for x in value]
                    self.params.append("{}={}".format(urllib.parse.quote_plus(key),
                                                      ','.join(properties)))
        elif isinstance(params, list):
            self.params += [urllib.parse.quote_plus(x) for x in params]
        else:
            self.params.append(urllib.parse.quote_plus(params))

    def add_data(self, data: dict):
        self.data.update(data)

    def get(self) -> Response:
        url = f"{self.server}/{self.url}"
        if self.params:
            url += f"?{'&'.join(self.params)}"
        data = None
        if self.method == RequestType.POST:
            data = urllib.parse.urlencode(self.data)
            data = data.encode("ascii")
        response = urllib.request.urlopen(url, data)
        if response.status == 200:
            response = Response(ResponseType.SUCCESS, response.read())
        else:
            response = Response(ResponseType.ERROR, response.reason)

        return response

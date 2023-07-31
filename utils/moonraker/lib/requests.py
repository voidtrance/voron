import urllib.parse
import urllib.request
import json
import enum
from os.path import basename
import requests
from . import encoder


@enum.unique
class RequestType(enum.StrEnum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


@enum.unique
class ResponseType(enum.IntEnum):
    SUCCESS = enum.auto()
    ERROR = enum.auto()


class Response:
    def __init__(self, _response: requests.Response, _stream: bool):
        if _response.status_code >= 200 and \
                _response.status_code < 300:
            self.status = ResponseType.SUCCESS
        else:
            self.status = ResponseType.ERROR
        self.status_code = _response.status_code
        self.reason = None
        self.data = None
        self.content_type = _response.headers["Content-Type"]
        if self.status == ResponseType.SUCCESS:
            if not _stream:
                if self.content_type.startswith("application/json"):
                    data = json.loads(_response.text)
                    if "result" in data:
                        self.data = data["result"]
                    else:
                        self.data = data
                elif self.content_type == "text/plain":
                    self.data = _response.text
            else:
                self.__response = _response
        else:
            self.reason = _response.reason

    def read(self, bytes: int) -> iter:
        return self.__response.iter_content(bytes)


class Request:
    def __init__(self, server: str, url: str, method: RequestType = RequestType.GET,
                 streaming=False):
        self.server = server
        self.url = url
        self.method = method
        self.data = {}
        self.params = []
        self.headers = {}
        self.files = []
        self.streaming_request = streaming

    def add_params(self, params: str | list | dict) -> None:
        if isinstance(params, dict):
            for key, value in params.items():
                if not value:
                    self.params.append(urllib.parse.quote_plus(key))
                else:
                    if isinstance(value, list):
                        properties = [urllib.parse.quote_plus(x)
                                      for x in value]
                    else:
                        properties = [urllib.parse.quote_plus(value)]
                    self.params.append("{}={}".format(urllib.parse.quote_plus(key),
                                                      ','.join(properties)))
        elif isinstance(params, list):
            self.params += [urllib.parse.quote_plus(x) for x in params]
        else:
            self.params.append(urllib.parse.quote_plus(params))

    def add_header(self, headers: dict) -> None:
        self.headers.update(headers)

    def add_data(self, data: dict) -> None:
        self.data.update(data)

    def add_file(self, key, file: str) -> None:
        self.files.append((key, file))
        self.method = RequestType.POST

    def get(self) -> Response:
        url = f"{self.server}/{self.url}"
        if self.params:
            url += f"?{'&'.join(self.params)}"
        data = None
        data = self.data
        if self.method == RequestType.POST:
            if self.files:
                for f in self.files:
                    data[f[0]] = (basename(f[1]), open(f[1], 'rb'),
                                  "application/octet-stream")
        enc = encoder.MultipartEncoder(data)
        self.headers.update({"Content-Type": enc.content_type})
        try:
            r = requests.request(str(self.method), url, headers=self.headers,
                                 data=enc, stream=self.streaming_request)
            response = Response(r, self.streaming_request)
        except requests.exceptions.ConnectionError as e:
            raise e

        return response

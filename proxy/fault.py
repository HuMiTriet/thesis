from abc import abstractmethod
from dataclasses import dataclass
from time import sleep
from requests import Response

from flask.wrappers import Request


@dataclass(slots=True, kw_only=True)
class Fault:
    name: str
    condition: str

    @abstractmethod
    def execute(self, request: Request, url: str):
        pass


# needs to get in the url and request.method
@dataclass(slots=True, kw_only=True)
class DelayFault(Fault):
    duration: float

    def execute(self, request: Request, url: str):
        if eval(self.condition):
            sleep(self.duration)


@dataclass(slots=True, kw_only=True)
class ErrorFault(Fault):
    text: str = "Intentional error"
    status_code: int = 420

    def execute(self, request: Request, url: str):
        if eval(self.condition):
            return self.text, self.status_code
        else:
            pass

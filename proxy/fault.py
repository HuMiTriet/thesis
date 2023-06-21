from abc import abstractmethod
import asyncio
from dataclasses import dataclass

# from time import sleep
import re  # pyright: ignore # pylint: disable=unused-import # noqa

from flask.wrappers import Request


@dataclass(slots=True, kw_only=True)
class Fault:
    name: str
    condition: str

    @abstractmethod
    async def execute(self, request: Request, url: str):
        pass


# needs to get in the url and request.method
@dataclass(slots=True, kw_only=True)
class DelayFault(Fault):
    duration: float

    async def execute(
        self,
        request: Request,
        url: str,
    ):  # pyright: ignore
        # pylint: disable=eval-used
        if eval(self.condition):
            await asyncio.sleep(self.duration)


@dataclass(slots=True, kw_only=True)
class ErrorFault(Fault):
    text: str = "Intentional error"
    status_code: int = 420

    # pylint: disable=inconsistent-return-statements
    async def execute(
        self,
        request: Request,  # pyright: ignore
        url: str,  # pyright: ignore
    ):
        # pylint: disable=eval-used
        if eval(self.condition):
            return self.text, self.status_code

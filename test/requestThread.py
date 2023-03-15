from threading import Thread
from typing import Callable, Iterable, Mapping, Any
from requests import Response


class RequestsThread(Thread):
    def __init__(
        self,
        group=None,
        target: Callable[..., object] | None = ...,
        name: str | None = ...,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] = ...,
        *,
        daemon: bool | None = ...,
    ) -> None:
        # super().__init__(group, target, name, args, kwargs, daemon=daemon)
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._response = Response
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        if self._target is not None:
            self._response = self._target(**self._kwargs)

    def join(self, *args) -> Response:
        Thread.join(self, *args)
        return self._response

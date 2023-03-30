import os
from dataclasses import field, dataclass
import requests

from flask import json


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


@dataclass
class InjectibleFault:
    fault_names: list[str] = field(default_factory=list[str])

    # def __init__(self, fault_names: list[str]) -> None:
    #     self.fault_names = fault_names

    def __enter__(self):
        requests.post(
            "http://127.0.0.1:5004/inject",
            json=json.dumps(self.fault_names),
            timeout=TIMEOUT,
        )

    def __exit__(
        self,
        *args,  # pyright: ignore
    ):
        requests.delete(
            "http://127.0.0.1:5004/inject",
            timeout=TIMEOUT,
        )

from proxy.fault import Fault
import requests

from flask import json


class InjectibleFault(object):
    def __init__(self, fault_names: list[str]) -> None:
        self.fault_names = fault_names

    def __enter__(self):
        requests.post(
            "http://127.0.0.1:5004/inject",
            json=json.dumps(self.fault_names),
        )

    def __exit__(self, *args):
        requests.delete(
            "http://127.0.0.1:5004/inject",
        )

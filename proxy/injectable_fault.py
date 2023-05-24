import os
from dataclasses import field, dataclass
import requests


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


@dataclass
class InjectibleFault:
    fault_names: list[str] = field(default_factory=list[str])

    def __enter__(self):

        print(f"fault to be inject (InjectibleFault) {self.fault_names}")

        requests.post(
            "http://127.0.0.1:5004/inject",
            json={"fault": self.fault_names},
        )

    def __exit__(
        self,
        *args,  # pyright: ignore
    ):
        requests.delete(
            "http://127.0.0.1:5004/inject",
        )

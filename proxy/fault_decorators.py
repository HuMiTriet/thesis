from collections.abc import Callable
from functools import wraps
from typing import Any
from flask import json

import requests


"""Fault injection decorator, The effect will be delegated to the proxy"""


def fault_injection(fault_names: list[str]):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Adds in fault to the currently injecting faults"""

            # print("DECOR BEING CALLED")

            requests.post(
                "http://127.0.0.1:5004/inject",
                json=json.dumps(fault_names),
            )

            # try construct here
            func(*args, **kwargs)

            # print("DECOR STOP BEING CALLED")

            # Put clean up in final clause
            """Remove the faults once done"""
            # managerState.faults_currently_injected.clear()
            requests.delete(
                "http://127.0.0.1:5004/inject",
            )

        return wrapper

    return decorator

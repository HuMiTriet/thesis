import os
from collections.abc import Callable
from functools import wraps
from typing import Any

import requests

TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


def fault_injection(fault_names: list[str]):
    """Fault injection decorator, The effect will be delegated to the proxy"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Adds in fault to the currently injecting faults

            requests.post(
                "http://127.0.0.1:5001/inject",
                json={"fault": fault_names},
                timeout=TIMEOUT,
            )

            # print(f"injected fault {fault_names} into proxy")

            # try construct here
            func(*args, **kwargs)

            # print("DECOR STOP BEING CALLED")

            # Put clean up in final clause
            # Remove the faults once done
            # managerState.faults_currently_injected.clear()
            requests.delete(
                "http://127.0.0.1:5001/inject",
                timeout=TIMEOUT,
            )

        return wrapper

    return decorator

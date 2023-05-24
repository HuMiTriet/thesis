import asyncio
import json
import os
import requests
import pytest
from .stratergies import RuleBaseInjectibleFault

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x: list[float] = []  # change this to input delay and value


def test_client_with_delay(
    setup_ricart_agrawala_four_client,
    # setup_ricart_agrawala_four_client_and_load_faults,
    # setup_maekawa_four_client_and_load_faults,
    # setup_four_token_and_load_faults,
    # load_faults_into_proxy,
):
    fault = RuleBaseInjectibleFault()

    for _ in range(10):
        client_request_with_delay(fault, 1)
        client_request_with_delay(fault, 2)
        client_request_with_delay(fault, 3)
        client_request_with_delay(fault, 4)
        client_request_with_delay(fault, 5)
        client_request_with_delay(fault, 6)
        client_request_with_delay(fault, 7)
        client_request_with_delay(fault, 8)
        client_request_with_delay(fault, 9)
        client_request_with_delay(fault, 10)
        client_request_with_delay(fault, 11)
        client_request_with_delay(fault, 12)
        client_request_with_delay(fault, 13)
        client_request_with_delay(fault, 14)
        client_request_with_delay(fault, 15)
        client_request_with_delay(fault, 16)
        client_request_with_delay(fault, 17)
        client_request_with_delay(fault, 18)
        client_request_with_delay(fault, 19)
        client_request_with_delay(fault, 20)

    with open(
        os.path.join("ricart_agrawala_median.json"),
        "w",
        encoding="utf-8"
        # os.path.join("ricart_agrawala.json"), "w", encoding="utf-8",
    ) as file:
        file.write(json.dumps(x))


def client_request_with_delay(fault: RuleBaseInjectibleFault, times: int):
    fault_times: list[str] = []
    for _ in range(times):
        fault_times.append("delay_all_small")

    fault.inject(fault_times)

    client_request(5002)  # start A
    requests.delete("http://127.0.0.1:5002/A/lock", timeout=10)  # end

    client_request(5003)
    requests.delete("http://127.0.0.1:5003/A/lock", timeout=10)

    client_request(5004)
    requests.delete("http://127.0.0.1:5004/A/lock", timeout=10)

    client_request(5005)
    requests.delete("http://127.0.0.1:5005/A/lock", timeout=10)

    # resp = requests.get("http://127.0.0.1:3000/stat")
    resp = requests.get("http://127.0.0.1:3000/stat_median")
    # resp = requests.get("http://127.0.0.1:3000/stat_mean")

    x.extend(resp.json())
    fault.reset()


def client_request(port: int):
    requests.post(
        f"http://127.0.0.1:{port}/A/request",
    )

    requests.post(
        f"{SERVER_URL}reset",
    )

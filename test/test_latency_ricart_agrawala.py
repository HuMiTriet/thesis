import asyncio
import json
import os
import requests
import pytest
from .stratergies import RuleBaseInjectibleFault

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x = []


def test_client_with_delay(
    # setup_ricart_agrawala_four_client,
    # setup_ricart_agrawala_four_client_and_load_faults,
    # setup_maekawa_four_client_and_load_faults,
    # setup_four_token_and_load_faults,
    # load_faults_into_proxy,
):
    fault = RuleBaseInjectibleFault()

    for _ in range(10):
        client_request_with_delay(fault, "0.01")
        client_request_with_delay(fault, "0.02")
        client_request_with_delay(fault, "0.03")
        client_request_with_delay(fault, "0.04")
        client_request_with_delay(fault, "0.05")
        client_request_with_delay(fault, "0.06")
        client_request_with_delay(fault, "0.07")
        client_request_with_delay(fault, "0.08")
        client_request_with_delay(fault, "0.09")
        client_request_with_delay(fault, "0.1")
        client_request_with_delay(fault, "0.11")
        client_request_with_delay(fault, "0.12")
        client_request_with_delay(fault, "0.13")
        client_request_with_delay(fault, "0.14")
        client_request_with_delay(fault, "0.15")
        client_request_with_delay(fault, "0.16")
        client_request_with_delay(fault, "0.17")
        client_request_with_delay(fault, "0.18")
        client_request_with_delay(fault, "0.19")
        client_request_with_delay(fault, "0.2")

    with open(
        os.path.join("ricart_agrawala_median.json"),
        "w",
        encoding="utf-8"
        # os.path.join("ricart_agrawala.json"), "w", encoding="utf-8",
    ) as file:
        file.write(json.dumps(x))


def client_request_with_delay(fault: RuleBaseInjectibleFault, delay_time: str):
    # for _ in range(times):
    #     fault_times.append("delay_all_small")

    fault_times: list[str] = []
    fault_times.append(delay_time)
    fault.inject(fault_times)

    client_request(5002, delay_time)  # start A
    requests.delete("http://127.0.0.1:5002/A/lock")  # end

    client_request(5003, delay_time)
    requests.delete("http://127.0.0.1:5003/A/lock")

    client_request(5004, delay_time)
    requests.delete("http://127.0.0.1:5004/A/lock")

    client_request(5005, delay_time)
    requests.delete("http://127.0.0.1:5005/A/lock")

    # resp = requests.get("http://127.0.0.1:3000/stat")
    resp = requests.get("http://127.0.0.1:3000/stat_median")
    # resp = requests.get("http://127.0.0.1:3000/stat_mean")

    data = resp.json()
    result = {
        "latency": data["median_latency"],
        "delay_time": data["delay_time"],
    }

    x.append(result)
    fault.reset()


def client_request(port: int, delay_time: str):
    requests.post(
        f"http://127.0.0.1:{port}/A/request",
        json={
            "delay_time": delay_time,
        },
    )

    requests.post(
        f"{SERVER_URL}reset",
    )

import asyncio
import json
import os
from time import sleep
from hypothesis import given, strategies as st
import requests
import pytest
from proxy.fault_decorators import fault_injection
from .stratergies import RuleBaseInjectibleFault

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x = []


def test_client_with_delay(
    setup_maekawa_four_client,
    # setup_maekawa_four_client_and_load_faults,
    # setup_four_token_and_load_faults,
    # load_faults_into_proxy,
):
    for _ in range(10):
        client_request_with_delay("0.0")
        client_request_with_delay("0.01")
        client_request_with_delay("0.02")
        client_request_with_delay("0.03")
        client_request_with_delay("0.04")
        client_request_with_delay("0.05")
        client_request_with_delay("0.06")
        client_request_with_delay("0.07")
        client_request_with_delay("0.08")
        client_request_with_delay("0.09")
        client_request_with_delay("0.1")
        client_request_with_delay("0.11")
        client_request_with_delay("0.12")
        client_request_with_delay("0.13")
        client_request_with_delay("0.14")
        client_request_with_delay("0.15")
        client_request_with_delay("0.16")
        client_request_with_delay("0.17")
        client_request_with_delay("0.18")
        client_request_with_delay("0.19")
        client_request_with_delay("0.2")

    with open(
        os.path.join("maekawa_median.json"), "w", encoding="utf-8"
    ) as file:
        file.write(json.dumps(x))


def client_request_with_delay(delay_time: str):
    client_request(5002, delay_time)  # start A
    requests.delete(
        "http://127.0.0.1:5002/A/lock",
        json={
            "delay_time": delay_time,
        },
    )

    client_request(5003, delay_time)
    requests.delete(
        "http://127.0.0.1:5003/A/lock",
        json={
            "delay_time": delay_time,
        },
    )

    client_request(5004, delay_time)
    requests.delete(
        "http://127.0.0.1:5004/A/lock",
        json={
            "delay_time": delay_time,
        },
    )

    client_request(5005, delay_time)
    requests.delete(
        "http://127.0.0.1:5005/A/lock",
        json={
            "delay_time": delay_time,
        },
    )

    resp = requests.get("http://127.0.0.1:3000/stat")
    # resp = requests.get("http://127.0.0.1:3000/stat_median")

    data = resp.json()
    # result = {
    #     "latency": data["median_latency"],
    #     "delay_time": data["delay_time"],
    # }

    x.extend(data)


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

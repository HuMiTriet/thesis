import asyncio
import json
import os
from hypothesis import given, strategies as st
import requests
import pytest
from proxy.fault_decorators import fault_injection
from .stratergies import RuleBaseInjectibleFault

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x: list[float] = []  # change this to input delay and value


pytest_plugins = ("asyncio",)


@pytest.mark.asyncio
async def test_client_with_delay(
    # setup_ricart_agrawala_four_client_and_load_faults,
    # setup_maekawa_four_client_and_load_faults,
    # setup_four_token_and_load_faults,
    # load_faults_into_proxy,
):
    for _ in range(10):
        await client_request_with_delay("0.0")
        await client_request_with_delay("0.01")
        await client_request_with_delay("0.02")
        await client_request_with_delay("0.03")
        await client_request_with_delay("0.04")
        await client_request_with_delay("0.05")
        await client_request_with_delay("0.06")
        await client_request_with_delay("0.07")
        await client_request_with_delay("0.08")
        await client_request_with_delay("0.09")
        await client_request_with_delay("0.1")
        await client_request_with_delay("0.11")
        await client_request_with_delay("0.12")
        await client_request_with_delay("0.13")
        await client_request_with_delay("0.14")
        await client_request_with_delay("0.15")
        await client_request_with_delay("0.16")
        await client_request_with_delay("0.17")
        await client_request_with_delay("0.18")
        await client_request_with_delay("0.19")
        await client_request_with_delay("0.2")
    with open(
        os.path.join("token_ring_median.json"), "w", encoding="utf-8"
    ) as file:
        file.write(json.dumps(x))


async def client_request_with_delay(delay_time: str):
    client_request(5002, delay_time)
    client_request(5003, delay_time)
    client_request(5004, delay_time)
    client_request(5005, delay_time)

    await asyncio.sleep(3)

    resp = requests.get("http://127.0.0.1:3000/stat")

    x.extend(resp.json())


def client_request(port: int, delay_time: str):
    requests.post(
        f"http://127.0.0.1:{port}/A/request",
        json={
            "delay_time": delay_time,
        },
    )

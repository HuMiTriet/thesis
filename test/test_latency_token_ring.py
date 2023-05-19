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

x: list[float] = []  # change this to input delay and value


pytest_plugins = ("asyncio",)


@pytest.mark.asyncio
async def test_client_with_delay(
    # setup_ricart_agrawala_four_client_and_load_faults,
    # setup_maekawa_four_client_and_load_faults,
    # setup_four_token_and_load_faults,
    load_faults_into_proxy,
):
    fault = RuleBaseInjectibleFault()

    for _ in range(10):
        await client_request_with_delay(fault, 1)
        await client_request_with_delay(fault, 2)
        await client_request_with_delay(fault, 3)
        await client_request_with_delay(fault, 4)
        await client_request_with_delay(fault, 5)
        await client_request_with_delay(fault, 6)
        await client_request_with_delay(fault, 7)
        await client_request_with_delay(fault, 8)
        await client_request_with_delay(fault, 9)
        await client_request_with_delay(fault, 10)
        await client_request_with_delay(fault, 11)
        await client_request_with_delay(fault, 12)
        await client_request_with_delay(fault, 13)
        await client_request_with_delay(fault, 14)
        await client_request_with_delay(fault, 15)
        await client_request_with_delay(fault, 16)
        await client_request_with_delay(fault, 17)
        await client_request_with_delay(fault, 18)
        await client_request_with_delay(fault, 19)
        await client_request_with_delay(fault, 20)

    with open(
        os.path.join("token_ring_median.json"), "w", encoding="utf-8"
    ) as file:
        file.write(json.dumps(x))


async def client_request_with_delay(
    fault: RuleBaseInjectibleFault, times: int
):
    fault_times: list[str] = []
    for _ in range(times):
        fault_times.append("delay_all_small")

    fault.inject(fault_times)

    client_request(5002)

    client_request(5003)

    client_request(5004)

    client_request(5005)

    await asyncio.sleep(1)

    # resp = requests.get("http://127.0.0.1:3000/stat")
    resp = requests.get("http://127.0.0.1:3000/stat_median")

    x.extend(resp.json())
    fault.reset()


def client_request(port: int):
    requests.post(
        f"http://127.0.0.1:{port}/A/request",
        # timeout=10,
    )

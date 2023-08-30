import asyncio
import signal
import subprocess
import json
import os

import pytest
import requests
from .stratergies import RuleBaseInjectibleFault

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x = []

pytest_plugins = ("asyncio",)


@pytest.mark.asyncio
async def test_client_with_delay(
    setup_ricart_agrawala_four_client,
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
        # os.path.join("ricart_agrawala_median.json"), "w", encoding="utf-8"
        os.path.join("ricart_agrawala.json"),
        "w",
        encoding="utf-8",
    ) as file:
        file.write(json.dumps(x))


async def client_request_with_delay(delay_time: str):
    # fault.inject([f"{delay_time}"])
    # command = [
    #     "gunicorn",
    #     "--reload",
    #     "-w",
    #     "5",
    #     "-b",
    #     "127.0.0.1:5001",
    #     "proxy:create_app()",
    # ]
    # server = subprocess.Popen(command)
    await asyncio.sleep(2)

    # try:
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
    # resp = requests.get("http://127.0.0.1:3000/stat_mean")

    data = resp.json()
    # result = {
    #     "latency": data["latency"],
    #     "delay_time": data["delay_time"],
    # }

    x.extend(data)


# fault.reset()
# finally:
#     server.send_signal(signal.SIGINT)
#     server.wait()


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

import asyncio
import time
import pytest
import requests


# scalling_clients: list[int] = [10]
TIMEOUT = 100000
pytest_plugins = ("asyncio",)


scalling_clients: list[int] = list(range(4, 5))


@pytest.mark.parametrize("setup_ricart_scale", scalling_clients, indirect=True)
def test_ricart(setup_ricart_scale, result_aggregator):
    client_ports_number = setup_ricart_scale["client_ports_number"]
    numb_of_clients: str = str(len(client_ports_number))
    for client_port in client_ports_number:
        requests.post(
            f"http://127.0.0.1:{client_port}/A/request",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
            timeout=TIMEOUT,
        )

        requests.delete(
            f"http://127.0.0.1:{client_port}/A/lock",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
            timeout=TIMEOUT,
        )

    resp = requests.get(
        "http://127.0.0.1:3000/stat",
        timeout=TIMEOUT,
    )

    result_aggregator.extend(resp.json())


@pytest.mark.parametrize(
    "setup_maekawa_scale", scalling_clients, indirect=True
)
def test_maekawa(setup_maekawa_scale, result_aggregator):
    client_ports_number = setup_maekawa_scale["client_ports_number"]
    numb_of_clients: str = str(len(client_ports_number))
    for client_port in client_ports_number:
        requests.post(
            f"http://127.0.0.1:{client_port}/A/request",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
            timeout=TIMEOUT,
        )

        requests.delete(
            f"http://127.0.0.1:{client_port}/A/lock",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
            timeout=TIMEOUT,
        )

        # print(
        #     f"client {client_port} delete request with {rd.status_code} and {rd.text}"
        # )

    resp = requests.get(
        "http://127.0.0.1:3000/stat",
        timeout=TIMEOUT,
    )

    result_aggregator.extend(resp.json())


@pytest.mark.parametrize(
    "setup_token_ring_scale", scalling_clients, indirect=True
)
@pytest.mark.asyncio()
async def test_token_ring(
    setup_token_ring_scale,
    result_aggregator,
):
    client_ports_number = setup_token_ring_scale["client_ports_number"]
    numb_of_clients: str = str(len(client_ports_number))

    requests.put(
        "http://127.0.0.1:5002/A/token",
        json={
            "client_url": "http://127.0.0.1:5002/",
            "client_no": numb_of_clients,
        },
    )

    await asyncio.sleep(0.5)

    for client_port in client_ports_number:
        lock = requests.post(
            f"http://127.0.0.1:{client_port}/A/request",
            json={
                "client_url": f"http://127.0.0.1:{client_port}/",
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
            timeout=TIMEOUT,
        )

        print(
            f"client {client_port} lock request with {lock.status_code} and {lock.text}"
        )

        # unlock = requests.delete(
        #     f"http://127.0.0.1:{client_port}/A/lock",
        #     json={
        #         "delay_time": "0.0",
        #         "client_no": numb_of_clients,
        #     },
        #     timeout=TIMEOUT,
        # )

        # print(
        #     f"client {client_port} delete request with {unlock.status_code} and {unlock.text}"
        # )

        # await asyncio.sleep(1)

    resp = requests.get(
        "http://127.0.0.1:3000/stat",
        timeout=TIMEOUT,
    )

    print(resp.json())
    result_aggregator.extend(resp.json())

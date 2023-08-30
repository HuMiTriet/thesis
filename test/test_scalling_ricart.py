import json
import os
import pytest
import requests


scalling_clients: list[int] = list(range(4, 31))


@pytest.mark.parametrize("setup_ricart_scale", scalling_clients, indirect=True)
def test_client_scaling(setup_ricart_scale, result_aggregator):
    client_ports_number = setup_ricart_scale["client_ports_number"]
    numb_of_clients: str = str(len(client_ports_number))
    for client_port in client_ports_number:
        requests.post(
            f"http://127.0.0.1:{client_port}/A/request",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
        )

        requests.delete(
            f"http://127.0.0.1:{client_port}/A/lock",
            json={
                "delay_time": "0.0",
                "client_no": numb_of_clients,
            },
        )

    resp = requests.get("http://127.0.0.1:3000/stat")

    result_aggregator.extend(resp.json())

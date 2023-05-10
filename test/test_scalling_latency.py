import json
import os
import requests

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

x: list[float] = []


def test_four_client(
    setup_token_ring_four_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()


def test_five_client(
    setup_token_ring_five_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()


def test_six_client(
    setup_token_ring_six_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()
    # 7,


def test_seven_client(
    setup_token_ring_seven_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 8,


def test_8_client(
    setup_token_ring_8_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 9,


def test_9_client(
    setup_token_ring_9_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 10,


def test_10_client(
    setup_token_ring_10_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 11,


def test_11_client(
    setup_token_ring_11_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 12,


def test_12_client(
    setup_token_ring_11_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()

    # 13,


def test_13_client(
    setup_token_ring_12_client,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
):
    run_requests()


def test_write_result():
    with open(os.path.join("result.json"), "w", encoding="utf-8") as file:
        file.write(json.dumps(x))


def run_requests():

    client_request(5002)
    requests.delete("http://127.0.0.1:5002/A/lock", timeout=10)

    client_request(5003)
    requests.delete("http://127.0.0.1:5003/A/lock", timeout=10)

    client_request(5004)
    requests.delete("http://127.0.0.1:5004/A/lock", timeout=10)

    client_request(5005)
    requests.delete("http://127.0.0.1:5005/A/lock", timeout=10)

    resp = requests.get("http://127.0.0.1:3000/stat", timeout=10)

    x.extend(resp.json())


def client_request(port: int):
    requests.post(
        f"http://127.0.0.1:{port}/A/request",
        # timeout=10,
    )

    # requests.post(
    #     f"{SERVER_URL}reset",
    #     # timeout=TESTING_TIMEOUT,
    # )

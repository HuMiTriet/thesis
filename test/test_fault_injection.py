import os
from hypothesis import given, settings, strategies as st
from requests import Response
import requests

from proxy.fault_decorators import fault_injection
from .request_thread import RequestsThread

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


@fault_injection(["deplay_all_small", "error_420"])
@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
)
def test_one_client_lock(
    setup,  # pyright: ignore # pylint: disable=unused-argument
    register_client,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
    client_port: int,
):

    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )

    assert response.status_code == 401

    requests.delete(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )


@fault_injection(["delay_5002_no_reg"])
@given(resource_id=st.sampled_from(["A", "B"]))
def test_5002_no_registrar(
    setup,  # pyright: ignore # pylint: disable=unused-argument
    register_client,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
):

    response = requests.post(
        f"http://127.0.0.1:5002/{resource_id}/lock/no_registrar",
        timeout=TESTING_TIMEOUT,
    )

    assert response.status_code == 200

    requests.delete(
        f"http://127.0.0.1:5002/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )


# @fault_injection(["delay_5002_small"])
@fault_injection(["delay_5002_no_reg", "delay_5003_no_reg"])
@given(resource_id=st.sampled_from(["A", "B"]))
@settings(deadline=None)
def test_two_client_lock_no_reg(
    setup,  # pyright: ignore # pylint: disable=unused-argument
    register_client,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
):
    # def test_two_client_lock(resource_id: str):

    client_5002_thread = RequestsThread(
        target=requests.post,
        kwargs={
            "url": f"http://127.0.0.1:5002/{resource_id}/lock/no_registrar"
        },
    )

    client_5003_thread = RequestsThread(
        target=requests.post,
        kwargs={
            "url": f"http://127.0.0.1:5003/{resource_id}/lock/no_registrar"
        },
    )

    client_5002_thread.start()
    client_5003_thread.start()

    r_5002: Response = client_5002_thread.join()
    r_5003: Response = client_5003_thread.join()

    # assert not (r_5002.status_code == 200 and r_5003.status_code == 200)

    #    print(f" 5002 resp {r_5002.text} and stat {r_5002.status_code}")
    #    print(f" 5003 resp {r_5003.text} and stat {r_5003.status_code}")

    requests.delete(
        f"http://127.0.0.1:5002/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )
    requests.delete(
        f"http://127.0.0.1:5003/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )


@fault_injection(["delay_5002_small"])
@given(resource_id=st.sampled_from(["A", "B"]))
@settings(deadline=None)
def test_two_client_lock(
    setup,  # pyright: ignore # pylint: disable=unused-argument
    register_client,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
):

    client_1_thread = RequestsThread(
        target=requests.post,
        kwargs={"url": f"http://127.0.0.1:5002/{resource_id}/lock"},
    )

    client_2_thread = RequestsThread(
        target=requests.post,
        kwargs={"url": f"http://127.0.0.1:5003/{resource_id}/lock"},
    )

    client_1_thread.start()
    client_2_thread.start()

    r_1: Response = client_1_thread.join()
    r_2: Response = client_2_thread.join()

    #    print(f" 5002 resp {r_1.text} and code {r_1.status_code}")
    #    print(f" 5003 resp {r_2.text} and code {r_2.status_code}")

    # assert not (r_1.status_code == 200 and r_2.status_code == 200)

    requests.delete(
        f"http://127.0.0.1:5002/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )

    requests.delete(
        f"http://127.0.0.1:5003/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )

import os
from hypothesis import given, strategies as st
import requests
from flask.wrappers import Response
from .request_thread import RequestsThread

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
)
def test_one_client_lock(
    setup_no_registrar,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
    client_port: int,
):
    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock/no_registrar",
        timeout=TESTING_TIMEOUT,
    )
    # print(f"client {client_port} lock resource {resource_id}")
    assert response.status_code == 200

    requests.delete(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )


@given(resource_id=st.sampled_from(["A", "B"]))
def test_two_client_lock(
    setup_no_registrar,  # pyright: ignore # pylint: disable=unused-argument
    resource_id: str,
):

    client_1_thread = RequestsThread(
        target=requests.post,
        kwargs={
            "url": f"http://127.0.0.1:5002/{resource_id}/lock/no_registrar"
        },
    )

    client_2_thread = RequestsThread(
        target=requests.post,
        kwargs={
            "url": f"http://127.0.0.1:5003/{resource_id}/lock/no_registrar"
        },
    )

    client_1_thread.start()
    client_2_thread.start()

    r_1: Response = client_1_thread.join()
    r_2: Response = client_2_thread.join()

    # print(f"r_1 {r_1.status_code} and r_2 {r_2.status_code}")
    assert not (r_1.status_code == 200 and r_2.status_code == 200)

    requests.delete(
        f"http://127.0.0.1:5002/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )
    requests.delete(
        f"http://127.0.0.1:5003/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )

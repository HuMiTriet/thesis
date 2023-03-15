from hypothesis import given, strategies as st, note
import requests
from requests import Response
from .requestThread import RequestsThread


@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
)
def test_one_client_lock(
    setup_no_registrar, resource_id: str, client_port: int
):
    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock/no_registrar"
    )
    # print(f"client {client_port} lock resource {resource_id}")
    assert response.status_code == 200

    requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")


@given(resource_id=st.sampled_from(["A", "B"]))
def test_two_client_lock(resource_id: str):

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

    print(f"r_1 {r_1.status_code} and r_2 {r_2.status_code}")
    assert not (r_1.status_code == 200 and r_2.status_code == 200)

    requests.delete(f"http://127.0.0.1:5002/{resource_id}/lock")

    requests.delete(f"http://127.0.0.1:5003/{resource_id}/lock")

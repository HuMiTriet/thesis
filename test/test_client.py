from hypothesis import given, note, strategies as st
import requests
from requests import Response
from .requestThread import RequestsThread


@given(
    resource_id=st.sampled_from(["A", "B"]),
    # resource_id=resource(size=3),
    client_port=st.integers(min_value=5002, max_value=5003),
)
def test_one_client_lock(
    setup, register_client, resource_id: str, client_port: int
):

    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock"
    )
    # print(f"client {client_port} lock resource {resource_id}")

    assert response.status_code == 200

    requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")


@given(resource_id=st.sampled_from(["A", "B"]))
def test_client_do_not_release_currently_using(
    setup, register_client, resource_id: str
):
    r = requests.post(f"http://127.0.0.1:5002/{resource_id}/lock")
    # print(
    #     f"client 1 locking {resource_id} with text: {r.text} and status {r.status_code}"
    # )
    r = requests.post(f"http://127.0.0.1:5003/{resource_id}/lock")
    # print(
    #     f"client 2 locking {resource_id} with text: {r.text} and status {r.status_code}"
    # )
    # requests.delete(f"http://127.0.0.1:5003/{resource_id}/lock")
    r = requests.post(f"http://127.0.0.1:5002/{resource_id}/lock")
    # print(
    #     f"client 1 locking {resource_id} with text: {r.text} and status {r.status_code}"
    # )
    assert r.status_code == 200

    r = requests.delete(f"http://127.0.0.1:5002/{resource_id}/lock")


@given(resource_id=st.sampled_from(["A", "B"]))
def test_two_client_lock(setup, register_client, resource_id: str):

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

    print(f" 5002 resp {r_1.text} and code {r_1.status_code}")
    print(f" 5003 resp {r_2.text} and code {r_2.status_code}")
    assert not (r_1.status_code == 200 and r_2.status_code == 200)

    requests.delete(f"http://127.0.0.1:5002/{resource_id}/lock")
    requests.delete(f"http://127.0.0.1:5003/{resource_id}/lock")

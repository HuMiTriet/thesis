from hypothesis import given, settings, strategies as st, note
import requests


# putting the two tests below into a same class
class TestClientLock:

    # ascii code 65 = A, 66 = B because the dummy data only has 2 resources
    @given(resource_id=st.sampled_from(["A", "B"]))
    def test_get_resource_from_server(setup, resource_id: str) -> None:

        response = requests.get(f"http://127.0.0.1:5000/{resource_id}")
        # print(f"client get resource {resource_id} from server")
        assert response.status_code == 200 or response.status_code == 401

    @given(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5003),
    )
    def test_one_client_lock(
        setup, register_client, resource_id: str, client_port: int
    ):

        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock"
        )
        # print(f"client {client_port} lock resource {resource_id}")

        assert response.status_code == 200 or response.status_code == 401

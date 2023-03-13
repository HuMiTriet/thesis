from hypothesis import given, strategies as st
import requests


@given(resource_id=st.sampled_from(["A", "B"]))
def test_get_resource_from_server(setup, resource_id: str) -> None:

    response = requests.get(f"http://127.0.0.1:5000/{resource_id}")
    assert response.status_code == 200

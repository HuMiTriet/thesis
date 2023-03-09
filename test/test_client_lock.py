from hypothesis import HealthCheck, given, settings, strategies as st
import requests


# ascii code 65 = A, 66 = B because the dummy data only has 2 resources
@given(resource_id=st.characters(min_codepoint=65, max_codepoint=66))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_get_resource_from_server(setup, resource_id: str) -> None:

    response = requests.get(f"http://127.0.0.1:5000/{resource_id}")
    assert response.status_code == 200


@given(
    resource_id=st.characters(min_codepoint=65, max_codepoint=66),
    client_port=st.integers(min_value=5002, max_value=5003),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_one_client_lock(
    setup, register_client, resource_id: str, client_port: int
):
    requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")

    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock"
    )

    assert response.status_code == 200 or response.status_code == 403

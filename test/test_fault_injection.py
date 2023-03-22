from hypothesis import given, strategies as st
import requests

from proxy.fault_decorators import fault_injection

# from proxy.fault_decorators import decorator


@fault_injection(["error_420"])
@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
)
def test_one_client_lock(
    # setup,
    # register_client,
    resource_id: str,
    client_port: int,
):

    response = requests.post(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock"
    )
    # print(f"client {client_port} lock resource {resource_id}")

    assert response.status_code == 200

    requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")

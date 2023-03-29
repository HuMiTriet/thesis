from hypothesis.core import given
from hypothesis import given, settings, strategies as st
from .stratergies import fault_injection
from proxy.injectable_fault import InjectibleFault
import requests


@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
    fault=fault_injection(["deplay_all_small"]),
)
def test_one_client_lock(
    setup,
    register_client,
    resource_id: str,
    client_port: int,
    fault: InjectibleFault,
):

    with fault:
        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock"
        )

        assert response.status_code == 401

    requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")

import os
from hypothesis import given, settings, strategies as st
import requests
from proxy.injectable_fault import InjectibleFault
from .stratergies import fault_strategy


TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
    fault=fault_strategy(),
)
@settings(deadline=None)
def test_one_client_lock(
    setup,  # pylint: disable=unused-argument # pyright: ignore
    register_client,  # pylint: disable=unused-argument # pyright: ignore
    resource_id: str,
    client_port: int,
    fault: InjectibleFault,
):

    with fault:
        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )

        assert response.status_code in {401, 200}

    requests.delete(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )

import os
from hypothesis import given, strategies as st
import requests

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


@given(resource_id=st.sampled_from(["A", "B"]))
def test_get_resource_from_server(
    setup,  # pylint: disable=unused-argument # pyright: ignore
    resource_id: str,
) -> None:

    response = requests.get(
        f"http://127.0.0.1:5000/{resource_id}",
        timeout=TESTING_TIMEOUT,
    )
    assert response.status_code == 200

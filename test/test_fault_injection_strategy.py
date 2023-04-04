import os
from hypothesis import given, settings, strategies as st
import requests
from flask.wrappers import Response
from proxy.injectable_fault import InjectibleFault
from .stratergies import fault_strategy
from .request_thread import RequestsThread


TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


@given(
    resource_id=st.sampled_from(["A", "B"]),
    client_port=st.integers(min_value=5002, max_value=5003),
    fault=fault_strategy(),
)
@settings(deadline=None)
def test_one_client_lock(
    register_client,  # pylint: disable=unused-argument # pyright: ignore
    load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
    resource_id: str,
    client_port: int,
    fault: InjectibleFault,
):

    with fault:
        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )

        print(f"resp {response.text}")
        assert response.status_code == 200

    requests.delete(
        f"http://127.0.0.1:{client_port}/{resource_id}/lock",
        timeout=TESTING_TIMEOUT,
    )


@given(
    resource_id=st.sampled_from(["A", "B"]),
    fault=fault_strategy(),
)
@settings(deadline=None)
def test_two_client_lock(
    register_client,  # pylint: disable=unused-argument # pyright: ignore
    load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
    resource_id: str,
    fault: InjectibleFault,
):

    with fault:
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

        assert not (r_1.status_code == 200 and r_2.status_code == 200)

        requests.delete(
            f"http://127.0.0.1:5002/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )
        requests.delete(
            f"http://127.0.0.1:5003/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )

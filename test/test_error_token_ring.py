import os
import time
import requests
from proxy.fault_decorators import fault_injection

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))

testing_data: dict[str, float] = {}


@fault_injection(["error_420_5003"])
def test_one_client_lock_with_small_delay(
    # setup_token_ring_four_client,  # pylint: disable=unused-argument # pyright: ignore
    load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
):
    """
    This client is being injected with a 0.02 delay for all http requests
    """

    avg_duration = client_lock_10_times()

    assert avg_duration > 0
    print(f"average time taken to lock the resource is {avg_duration} second")
    testing_data["small"] = avg_duration


def client_lock_10_times() -> float:
    total_duration: float = 0

    for _ in range(10):

        start_time = time.time()

        requests.post(
            "http://127.0.0.1:5002/A/request",
            timeout=TESTING_TIMEOUT,
        )

        requests.put(
            "http://127.0.0.1:5003/A/token",
            timeout=TESTING_TIMEOUT,
        )

        requests.delete(
            "http://127.0.0.1:5002/A/lock",
            timeout=TESTING_TIMEOUT,
        )

        # assert r.status_code == 200

        # load the end_time from enviroment variables END_TIME
        end_time = float(os.environ.get("END_TIME", time.time()))

        duration = end_time - start_time

        total_duration += duration

    avg_duration = total_duration / 10

    return avg_duration

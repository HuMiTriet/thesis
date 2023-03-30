import os
import unittest
from requests import Response
from hypothesis import strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule
import pytest
import requests
from proxy.injectable_fault import InjectibleFault
from .request_thread import RequestsThread
from .stratergies import fault_strategy


pytestmark = pytest.mark.usefixtures("setup")
pytestmark = pytest.mark.usefixtures("register_client")

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "2"))


# the class should receive a setup fixture defined in the conftest.py file
# how to pass a fixture to a stateful test?
class LockingTest(RuleBasedStateMachine):
    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        fault=fault_strategy(),
    )
    def get_resource_from_server(
        self,
        resource_id: str,
        fault: InjectibleFault,
    ):
        with fault:
            response = requests.get(
                f"http://127.0.0.1:5000/{resource_id}",
                timeout=TESTING_TIMEOUT,
            )
            assert response.status_code == 200

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5003),
        fault=fault_strategy(),
    )
    def client_lock(
        self,
        resource_id: str,
        client_port: int,
        fault: InjectibleFault,
    ):

        with fault:
            response = requests.post(
                f"http://127.0.0.1:{client_port}/{resource_id}/lock",
                timeout=TESTING_TIMEOUT,
            )

            assert response.status_code == 200

            response = requests.delete(
                f"http://127.0.0.1:{client_port}/{resource_id}/lock",
                timeout=TESTING_TIMEOUT,
            )

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5003),
        fault=fault_strategy(),
    )
    def two_client_lock(
        self,
        resource_id: str,
        client_port: int,  # pylint: disable=unused-argument # pyright: ignore
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

            #    print(f" 5002 resp {r_1.text} and code {r_1.status_code}")
            #    print(f" 5003 resp {r_2.text} and code {r_2.status_code}")
            assert not (r_1.status_code == 200 and r_2.status_code == 200)

            requests.delete(
                f"http://127.0.0.1:5002/{resource_id}/lock",
                timeout=TESTING_TIMEOUT,
            )
            requests.delete(
                f"http://127.0.0.1:5003/{resource_id}/lock",
                timeout=TESTING_TIMEOUT,
            )


LockingTest.TestCase.settings = settings(max_examples=2, stateful_step_count=2)
LockingTestCase: unittest.TestCase = LockingTest.TestCase

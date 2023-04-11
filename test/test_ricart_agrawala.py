import os
import unittest
from hypothesis import strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
import requests
import pytest

from .request_thread import RequestsThread


pytestmark = pytest.mark.usefixtures("setup_lamport")

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))


class MutexLocking(RuleBasedStateMachine):
    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5004),
    )
    def test_request(
        self,
        resource_id: str,
        client_port: int,
    ):
        requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/request",
            timeout=10,
        )

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5004),
    )
    def test_unlock(
        self,
        resource_id: str,
        client_port: int,
    ):
        requests.delete(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock",
            timeout=10,
        )

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
    )
    def two_client(
        self,
        resource_id: str,
    ):
        client_1_thread = RequestsThread(
            target=requests.post,
            kwargs={"url": f"http://127.0.0.1:5002/{resource_id}/request"},
        )

        client_2_thread = RequestsThread(
            target=requests.post,
            kwargs={"url": f"http://127.0.0.1:5003/{resource_id}/request"},
        )

        client_1_thread.start()
        client_2_thread.start()

        response = requests.get(
            f"{SERVER_URL}race",
            timeout=TESTING_TIMEOUT,
        )

        assert response.status_code == 200

        requests.delete(
            f"http://127.0.0.1:5002/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )
        requests.delete(
            f"http://127.0.0.1:5003/{resource_id}/lock",
            timeout=TESTING_TIMEOUT,
        )

    @invariant()
    def test_no_race_server(self):
        response = requests.get(
            f"{SERVER_URL}race",
            timeout=TESTING_TIMEOUT,
        )

        assert response.status_code == 200


MutexLocking.TestCase.settings = settings(
    max_examples=10,
    stateful_step_count=4,
    deadline=None,
)
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

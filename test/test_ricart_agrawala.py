import os
import unittest
from hypothesis import strategies as st, settings
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
    initialize,
)
import requests
import pytest


from .stratergies import RuleBaseInjectibleFault

# pytestmark = pytest.mark.usefixtures("setup_ricart_agrawala_four_client")
pytestmark = pytest.mark.usefixtures(
    "setup_ricart_agrawala_four_client_and_load_faults"
)

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))


class MutexLocking(RuleBasedStateMachine):
    fault = RuleBaseInjectibleFault()

    @initialize()
    def inject_fault(self):
        fault_key = os.getenv("FAULT_KEY", "NULL")
        if fault_key != "NULL":
            self.fault.inject([fault_key])

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5005),
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
        client_port=st.integers(min_value=5002, max_value=5005),
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

    @invariant()
    def test_no_race_server(self):
        response = requests.get(
            f"{SERVER_URL}race",
            timeout=TESTING_TIMEOUT,
        )

        assert response.status_code == 200

    def teardown(self):
        requests.post(
            f"{SERVER_URL}reset",
            timeout=TESTING_TIMEOUT,
        )


MutexLocking.TestCase.settings = settings(
    max_examples=10,
    stateful_step_count=10,
    deadline=None,
)
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

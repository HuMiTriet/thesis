import os
import unittest
from hypothesis import strategies as st, settings, note
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
    initialize,
)
import requests
import pytest
from .stratergies import RuleBaseInjectibleFault


# pytestmark = pytest.mark.usefixtures("setup_maekawa_four_client")
pytestmark = pytest.mark.usefixtures(
    "setup_maekawa_four_client_and_load_faults"
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
        # fault=fault_strategy(),
    )
    def test_request(
        self,
        resource_id: str,
        client_port: int,
        # fault: InjectibleFault,
    ):
        # with fault:
        note(f"client {client_port} is attempting to lock {resource_id}")

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
        # fault: InjectibleFault,
    ):
        # with fault:
        note(f"client {client_port} is deleting {resource_id}")

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
    max_examples=50,
    stateful_step_count=50,
    deadline=None,
)
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

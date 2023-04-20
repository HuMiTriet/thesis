import os
import unittest
from hypothesis import strategies as st, settings, note
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
    precondition,
)
import requests
import pytest
from .stratergies import RuleBaseInjectibleFault, get_random_faults


# pytestmark = pytest.mark.usefixtures("setup_maekawa_four_client")

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))


class MutexLocking(RuleBasedStateMachine):
    just_ran_invariant = False
    fault = RuleBaseInjectibleFault()

    @rule(faults=get_random_faults())
    def inject_fault(self, faults):
        self.fault.inject(faults)

    @rule()
    def reset_faults(self):
        self.fault.reset()

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
        self.just_ran_invariant = False
        note(f"client {client_port} is attempting to lock {resource_id}")

        requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/request",
            timeout=10,
        )

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5005),
        # fault=fault_strategy(),
    )
    def test_unlock(
        self,
        resource_id: str,
        client_port: int,
        # fault: InjectibleFault,
    ):
        # with fault:
        self.just_ran_invariant = False
        note(f"client {client_port} is deleting {resource_id}")

        requests.delete(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock",
            timeout=10,
        )

    @precondition(lambda self: self.just_ran_invariant is False)
    @invariant()
    def test_no_race_server(self):
        self.just_ran_invariant = True

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

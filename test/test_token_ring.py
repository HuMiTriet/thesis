import os
import unittest
from hypothesis import strategies as st, settings, note

from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    # precondition,
)

import requests
import pytest

from .stratergies import RuleBaseInjectibleFault


pytestmark = pytest.mark.usefixtures("setup_four_token_and_load_faults")
# pytestmark = pytest.mark.usefixtures("setup_token_ring_four_client")

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))


class MutexLocking(RuleBasedStateMachine):
    # just_ran_invariant = False
    # last_operation = None
    fault = RuleBaseInjectibleFault()

    @initialize()
    def inject_fault(self):
        # pass
        fault_key = os.getenv("FAULT_KEY", "NULL")
        if fault_key != "NULL":
            self.fault.inject([fault_key])
        # self.fault.inject(["delay_all_small"])
        # self.fault.inject(["delay_all_medium"])
        # self.fault.inject(["delay_all_large"])

    @initialize(
        # resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5005),
    )
    def pass_in_token_a(
        self,
        # resource_id: str,
        client_port: int,
    ):
        requests.put(
            f"http://127.0.0.1:{client_port}/A/token",
            timeout=10,
        )
        note(f"passed token A to {client_port}")

    @initialize(
        # resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5005),
    )
    def pass_in_token_b(
        self,
        # resource_id: str,
        client_port: int,
    ):
        requests.put(
            f"http://127.0.0.1:{client_port}/B/token",
            timeout=10,
        )
        note(f"passed token B to {client_port}")

    # @rule()
    # def reset_faults(self):
    #     self.fault.reset()

    # @precondition(lambda self: self.last_operation != "request")
    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5005),
    )
    def test_request(
        self,
        resource_id: str,
        client_port: int,
    ):
        # with fault:
        # self.just_ran_invariant = False
        # self.last_operation = "request"
        note(f"client {client_port} is attempting to lock {resource_id}")

        requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/request",
            timeout=10,
        )

    # @precondition(lambda self: self.last_operation != "unlock")
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
        # self.just_ran_invariant = False
        # self.last_operation = "unlock"
        note(f"client {client_port} is deleting {resource_id}")
        # print(f"client {client_port} is deleting {resource_id}")

        requests.delete(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock",
            timeout=10,
        )

    # @precondition(lambda self: self.just_ran_invariant is False)
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
    max_examples=25,
    stateful_step_count=25,
    deadline=None,
)
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

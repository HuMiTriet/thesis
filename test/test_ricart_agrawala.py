import unittest
import aiohttp
from flask.wrappers import Response
from hypothesis import strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
import pytest
import requests
from .stratergies import fault_strategy

pytestmark = pytest.mark.usefixtures("setup_lamport")


class MutexLocking(RuleBasedStateMachine):
    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5003),
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
        client_port=st.integers(min_value=5002, max_value=5003),
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
        pass


MutexLocking.TestCase.settings = settings(
    max_examples=10,
    stateful_step_count=4,
    deadline=None,
)
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

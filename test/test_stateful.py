import unittest
from hypothesis import strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule
import pytest


import requests

from proxy.fault_decorators import fault_injection

pytestmark = pytest.mark.usefixtures("setup")
pytestmark = pytest.mark.usefixtures("register_client")


# the class should receive a setup fixture defined in the conftest.py file
# how to pass a fixture to a stateful test?
class LockingTest(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()

    @rule(resource_id=st.sampled_from(["A", "B"]))
    def get_resource_from_server(self, resource_id):
        response = requests.get(f"http://127.0.0.1:5000/{resource_id}")
        assert response.status_code == 200

    @rule(
        resource_id=st.sampled_from(["A", "B"]),
        client_port=st.integers(min_value=5002, max_value=5003),
    )
    def client_lock(self, resource_id: str, client_port: int):

        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock"
        )

        assert response.status_code == 200

        response = requests.delete(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock"
        )


LockingTest.TestCase.settings = settings(max_examples=2, stateful_step_count=4)
LockingTestCase: unittest.TestCase = LockingTest.TestCase

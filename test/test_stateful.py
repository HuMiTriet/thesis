import unittest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize
import pytest


import requests

from test.conftest import server_app


# the class should receive a setup fixture defined in the conftest.py file
# how to pass a fixture to a stateful test?
class LockingTest(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()

    @rule(resource_id=st.characters(min_codepoint=65, max_codepoint=66))
    def get_resource_from_server(self, resource_id):
        response = requests.get(f"http://127.0.0.1:5000/{resource_id}")
        print(response.status_code)
        assert response.status_code == 200

    @rule(
        resource_id=st.characters(min_codepoint=65, max_codepoint=66),
        client_port=st.integers(min_value=5002, max_value=5003),
    )
    def client_lock(self, resource_id: str, client_port: int):
        # requests.delete(f"http://127.0.0.1:{client_port}/{resource_id}/lock")
        response = requests.post(
            f"http://127.0.0.1:{client_port}/{resource_id}/lock"
        )
        assert response.status_code == 200 or response.status_code == 401


LockingTestCase: unittest.TestCase = LockingTest.TestCase

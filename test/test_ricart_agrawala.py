import os
import json
import unittest
from hypothesis import strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
import pytest
import requests


pytestmark = pytest.mark.usefixtures("setup_lamport")

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")
TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))


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
        response = requests.get(
            f"{SERVER_URL}race",
            timeout=TESTING_TIMEOUT,
        )

        assert response.status_code == 200

    def teardown(self):
        with open(
            os.path.join("dummy_data.json"), "r", encoding="utf-8"
        ) as file:
            data = json.load(file)

        for item in data:
            if item["is_locked"]:
                item["is_locked"] = False

        with open(
            os.path.join("dummy_data.json"), "w", encoding="utf-8"
        ) as file:
            json.dump(data, file)
        return super().teardown()


# MutexLocking.TestCase.settings = settings(
#     max_examples=10,
#     stateful_step_count=4,
#     deadline=None,
# )
MutexLockingCase: unittest.TestCase = MutexLocking.TestCase

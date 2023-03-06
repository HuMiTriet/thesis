import pytest
import requests


# run this setup once before all test
@pytest.fixture(scope="session", autouse=True)
def setup():

    print("Registering client 1")
    requests.post("http://127.0.0.1:5002/register")
    print("Registering client 2")
    requests.post("http://127.0.0.1:5003/register")


# using client 1 at 5002 to lock resource A, using form data
def test_lock_resource_A():
    print("Client 1 locking resource A")
    r = requests.post("http://127.0.0.1:5002/A/lock")
    print(r.text)
    assert r.status_code == 200

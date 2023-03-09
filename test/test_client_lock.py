import requests


def register():
    response = requests.post("http://127.0.0.1:5002/register")
    assert response.status_code == 200

    response = requests.post("http://127.0.0.1:5003/register")
    assert response.status_code == 200


def test_client_lock(setup):
    register()

    response = requests.post(
        "http://127.0.0.1:5002/resource_status", json={"resource_id": "A"}
    )
    assert response.status_code == 200

    response = requests.post(
        "http://127.0.0.1:5003/resource_status", json={"resource_id": "A"}
    )
    assert response.status_code == 200

    response = requests.post("http://127.0.0.1:5002/A/lock")
    assert response.status_code == 200

    response = requests.post("http://127.0.0.1:5003/A/lock")
    assert response.status_code == 403

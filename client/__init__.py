from flask import Flask
import requests

SERVER_URL = "http://127.0.0.1:5000/"
REGISTRAR_URL = "http://127.0.0.1:5001/"

resource_currently_using = []


def lock_resource(id: str, requester_url: str) -> requests.models.Response:
    r = requests.put(f"{SERVER_URL}{id}/lock", json={"origin": requester_url})
    return r


def broadcast_request(resource_id: str):
    r = requests.post(
        f"{REGISTRAR_URL}/broadcast", json={"resource_id": resource_id}
    )
    return r


def unlock_resource(id: str) -> requests.models.Response:
    r = requests.delete(f"{SERVER_URL}{id}/lock")
    return r


def update_resource(
    id: str, new_json_data: dict[str, str | bool]
) -> requests.models.Response:
    r = requests.put(
        f"{SERVER_URL}{id}",
        json=new_json_data,
    )
    return r


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import gossip

    app.register_blueprint(gossip.bp)

    return app

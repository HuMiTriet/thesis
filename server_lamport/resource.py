from dataclasses import dataclass, field
import os
from time import time

from flask import Blueprint, request
import requests


TIMEOUT_SEC: int = 10

REQUEST_TIMEOUT: float = float(os.getenv("TIMEOUT", "10"))

LOGGER_URL: str = os.getenv("LOGGER_URL", "http://127.0.0.1:3000/")

bp = Blueprint("resouce", __name__)


@dataclass(slots=True)
class ServerState:
    race_condition: bool = False
    resource: dict[str, bool] = field(default_factory=dict[str, bool])


server_state = ServerState()
server_state.resource = {"A": False, "B": False}


@bp.route("/race", methods=["GET"])
def check_race():
    if server_state.race_condition:
        return "race condition has occured", 418

    return "alles gut", 200


@bp.route("/<string:resource_id>", methods=["GET"])
def get(resource_id: str):
    potential_state = server_state.resource.get(resource_id)
    if potential_state is not None:
        return f"resource {resource_id} locking status {potential_state}", 200

    return "Resource not found", 404


@bp.route("/<string:resource_id>/is_lock", methods=["GET"])
def check_locking_status(resource_id: str):
    potential_state = server_state.resource.get(resource_id)
    if potential_state is not None:
        if potential_state:
            return f"resource {resource_id} is being locked", 423

        return f"resource {resource_id} is not being locked", 200

    return "Resource not found", 404


# accquire a temporary lock on a resource that will expirce after 2s
@bp.route("/<string:resource_id>/lock", methods=["PUT"])
def lock(resource_id: str):
    data = request.get_json()

    print(f"received lock from {data['client_url']}")

    requests.put(
        f"{LOGGER_URL}{resource_id}/log",
        json={
            "type": "end",
            "time": time(),
            "delay_time": data["delay_time"],
            "client_no": data["client_no"],
            "client_url": data["client_url"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    return "Resource locked", 200


# explicitly release a lock on a resource
@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
def unlock(resource_id: str):
    if resource_id in server_state.resource.keys():
        server_state.resource[resource_id] = False

        data = request.get_json()

        requests.put(
            f"{LOGGER_URL}{resource_id}/log",
            json={
                "type": "end",
                "client_url": data["client_url"],
                "time": time(),
                "delay_time": data["delay_time"],
                "client_no": data["client_no"],
            },
            timeout=REQUEST_TIMEOUT,
        )

        return f"sucessfully unlocked {resource_id}", 200
    return "Resource not found", 404


@bp.route("/reset", methods=["POST"])
def reset_resource():
    for resource in server_state.resource.keys():
        server_state.resource[resource] = False
    return "finish resetting", 200

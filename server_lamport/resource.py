from dataclasses import dataclass, field
import os


from flask import Blueprint


TIMEOUT_SEC: int = 10

REQUEST_TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5004")

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


# accquire a temporary lock on a resource that will expirce after 2s
@bp.route("/<string:resource_id>/lock", methods=["PUT"])
def lock(resource_id: str):

    potential_state = server_state.resource.get(resource_id)
    if potential_state is not None:
        if potential_state is True:
            server_state.race_condition = True
            return (
                f"Race condition: {resource_id} currently locked",
                423,
            )

        server_state.resource[resource_id] = True
        return f"sucessfully locked {resource_id}", 200

    return "Resource not found", 404


# explicitly release a lock on a resource
@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
def unlock(resource_id: str):

    try:
        server_state.resource[resource_id] = False
        return f"sucessfully unlocked {resource_id}", 200
    except KeyError:
        return "Resource not found", 404


@bp.route("/reset", methods=["POST"])
def reset_resource():
    for resource in server_state.resource.keys():
        server_state.resource[resource] = False
    return "finish resetting", 200

import os
from flask import Blueprint, request
import requests

from proxy import proxies
from . import resource_currently_using


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

bp = Blueprint("gossip", __name__)


# register its url with the registrar
@bp.route("/register", methods=["POST"])
def register():
    """
    This is used in the registrar version. Each client register to the
    registrar
    """

    response = requests.post(
        f"{REGISTRAR_URL}/register",
        json={"origin": request.host_url},
        proxies=proxies,
        timeout=TIMEOUT,
    )

    return response.text, response.status_code


@bp.route("/<string:resource_id>/lock", methods=["POST"])
def lock(resource_id: str) -> tuple[str, int]:
    resource_currently_using.add(resource_id)

    try:
        response = requests.post(
            f"{REGISTRAR_URL}/{resource_id}/broadcast",
            json={
                "origin": request.host_url,
            },
            proxies=proxies,
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            lock_resource(resource_id, request.host_url)
            return (
                f"""resource {resource_id} is being
                locked by {request.host_url}""",
                200,
            )
    except requests.exceptions.Timeout as error:
        return str(error.__repr__), 403

    resource_currently_using.remove(resource_id)
    return response.text, 401


@bp.route("/<string:resource_id>/lock/no_registrar", methods=["POST"])
def lock_no_registrar(resource_id: str) -> tuple[str, int]:
    response = requests.put(
        f"{SERVER_URL}{resource_id}/lock",
        json={
            "origin": request.host_url,
        },
        proxies=proxies,
        timeout=TIMEOUT,
    )
    if response.status_code == 200:
        return (
            f"resource {resource_id} is being locked by {request.host_url}",
            200,
        )

    return response.text, response.status_code


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
def revoke_lock(resource_id: str):
    try:
        resource_currently_using.remove(resource_id)
        requests.delete(
            f"{SERVER_URL}/id/lock",
            proxies=proxies,
            timeout=TIMEOUT,
        )
        return (
            f"resource {resource_id} is being unlocked by {request.host_url}",
            200,
        )
    except KeyError:
        return "resource not locked", 412


# also send along with a priority
# implement stateful client
@bp.route("/<string:resource_id>/resource_status", methods=["GET"])
def resource_status(resource_id: str):

    if resource_id not in resource_currently_using:
        return "resource free", 200

    return "resource locked", 423


def lock_resource(
    resource_id: str,
    requester_url: str,
) -> requests.models.Response:
    response = requests.put(
        f"{SERVER_URL}{resource_id}/lock",
        json={"origin": requester_url},
        proxies=proxies,
        timeout=TIMEOUT,
    )
    return response

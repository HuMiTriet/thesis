from proxy import proxies
from . import resource_currently_using, lock_resource

from flask import Blueprint, request
import requests

SERVER_URL = "http://127.0.0.1:5000/"
REGISTRAR_URL = "http://127.0.0.1:5001/"


bp = Blueprint("gossip", __name__)


# register its url with the registrar
@bp.route("/register", methods=["POST"])
def register():
    r = requests.post(
        f"{REGISTRAR_URL}/register",
        json={"origin": request.host_url},
        proxies=proxies,
    )
    return r.text, r.status_code


@bp.route("/<string:id>/lock", methods=["POST"])
def lock(id: str) -> tuple[str, int]:
    resource_currently_using.add(id)

    r = requests.post(
        f"{REGISTRAR_URL}/{id}/broadcast",
        json={
            "origin": request.host_url,
        },
        proxies=proxies,
    )
    # how to do sth async here
    if r.status_code == 200:
        lock_resource(id, request.host_url)
        return f"resource {id} is being locked by {request.host_url}", 200
    else:
        resource_currently_using.remove(id)
        return r.text, 401


@bp.route("/<string:id>/lock/no_registrar", methods=["POST"])
def lock_no_registrar(id: str) -> tuple[str, int]:
    r = requests.put(
        f"{SERVER_URL}{id}/lock",
        json={
            "origin": request.host_url,
        },
        proxies=proxies,
    )
    if r.status_code == 200:
        return f"resource {id} is being locked by {request.host_url}", 200
    else:
        return r.text, r.status_code


@bp.route("/<string:id>/lock", methods=["DELETE"])
def revoke_lock(id: str):
    try:
        resource_currently_using.remove(id)
        requests.delete(
            f"{SERVER_URL}/id/lock",
            proxies=proxies,
        )
        return f"resource {id} is being unlocked by {request.host_url}", 200
    except KeyError:
        return "resource not locked", 412


# also send along with a priority
# implement stateful client
#
@bp.route("/<string:id>/resource_status", methods=["GET"])
def resource_status(id: str):
    print(
        f"""client {request.host_url} being ask {id} and
        current using {resource_currently_using}"""
    )
    if id not in resource_currently_using:
        return "resource free", 200
    else:
        return "resource locked", 423

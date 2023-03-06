from . import resource_currently_using, lock_resource

from flask import Blueprint, request
import requests

REGISTRAR_URL = "http://127.0.0.1:5001/"


bp = Blueprint("gossip", __name__)


# register its url with the registrar
@bp.route("/register", methods=["POST"])
def register():
    r = requests.post(
        f"{REGISTRAR_URL}/register",
        json={"url": request.host_url},
    )
    host_url = request.host_url
    return r.text, r.status_code


@bp.route("/<string:id>/lock", methods=["POST"])
def lock(id: str):
    r = requests.post(
        f"{REGISTRAR_URL}/broadcast",
        json={
            "url": request.host_url,
            "requested_id": id,
        },
    )
    if r.status_code == 200:
        lock_resource(id, request.host_url)
        resource_currently_using.append(id)
        return f"resource {id} is being locked by {request.host_url}", 200
    else:
        return "can't lock", 403


@bp.route("/<string:id>/lock", methods=["DELETE"])
def revoke_lock(id: str):
    try:
        resource_currently_using.remove(id)
        return f"resource {id} is being unlocked by {request.host_url}", 200
    except ValueError:
        return "resource not locked", 403


@bp.route("/resource_status", methods=["POST"])
def resource_status():
    data = request.get_json()
    id = data["resource_id"]
    if id not in resource_currently_using:
        return "resource free", 200
    else:
        return "resource locked", 423

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
    return r.text, r.status_code


@bp.route("/broadcast", methods=["POST"])
def broadcast():
    id: str = request.form["id"]
    r = requests.post(
        f"{REGISTRAR_URL}/broadcast",
        json={
            "url": request.host_url,
            "requested_id": id,
        },
    )
    if r.status_code == 200:
        lock_resource(id)
        resource_currently_using.append(id)
        return f"resource {id} is being locked by {request.host_url}", 200
    else:
        return "can't lock", 403


@bp.route("/resource_status", methods=["POST"])
def resource_status():
    data = request.get_json()
    id = data["resource_id"]
    if id not in resource_currently_using:
        return "resource free", 200
    else:
        return "resource locked", 423

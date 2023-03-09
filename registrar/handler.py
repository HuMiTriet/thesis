from flask import Blueprint
from flask import request
import requests


bp = Blueprint("handler", __name__)

subscribers_url: list[str] = []


@bp.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    print(request_data)
    subscribers_url.append(request_data["url"])
    return "subscribed", 200


@bp.route("/<string:resource_id>/broadcast", methods=["POST"])
def broadcast(resource_id: str):
    data = request.get_json()
    requester_url: str = data["url"]

    approvals: int = 0

    for url in subscribers_url:
        if url != requester_url:
            r = requests.post(
                f"{url}/{resource_id}/resource_status",
            )
            if r.status_code == 200:
                approvals += 1

    if approvals == len(subscribers_url) - 1:
        return "resource free", 200
    else:
        return "Someone reject the broadcast request", 417

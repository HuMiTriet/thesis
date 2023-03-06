from flask import Blueprint
from flask import request
import requests


bp = Blueprint("handler", __name__)

subscribers_url: list[str] = []

# subscribers_url.append("http://127.0.0.1:5002/")
# subscribers_url.append("http://127.0.0.1:5003/")


@bp.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    print(request_data)
    subscribers_url.append(request_data["url"])
    return "subscribed", 200


@bp.route("/broadcast", methods=["POST"])
def broadcast():
    data = request.get_json()
    requester_url: str = data["url"]
    resource_id: str = data["requested_id"]

    approvals: int = 0

    for url in subscribers_url:
        if url is not requester_url:
            r = requests.post(
                f"{url}/resource_status",
                json={"resource_id": resource_id},
            )
            if r.status_code == 200:
                approvals += 1

    if approvals == 1 or approvals == 2:
        return "resource free", 200
    else:
        return "resource locked", 423

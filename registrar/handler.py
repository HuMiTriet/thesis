from proxy import proxies
from flask import Blueprint
from flask import request
import requests


bp = Blueprint("handler", __name__)

subscribers_url: set[str] = set()


@bp.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
#    print(request_data)
    subscribers_url.add(request_data["url"])
#    print(f"full set of subs {subscribers_url}")
    return "subscribed", 200


@bp.route("/<string:resource_id>/broadcast", methods=["POST"])
def broadcast(resource_id: str):
    data = request.get_json()
    requester_url: str = data["url"]

    approvals: int = 0

    for url in subscribers_url:
        if url != requester_url:
            r = requests.get(
                f"{url}/{resource_id}/resource_status",
                json={},
                proxies=proxies,
            )
#            print(f"after broadcast {r.text}, {r.status_code}")
            if r.status_code == 200:
                approvals += 1
#                print(f"Registrar: received approval {resource_id} from {url}")

    if approvals == len(subscribers_url) - 1:
        return "resource free", 200
    else:
        return "Someone reject the broadcast request", 417

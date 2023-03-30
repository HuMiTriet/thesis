import os
from flask import Blueprint, request
import requests
from proxy import proxies


bp = Blueprint("handler", __name__)

subscribers_url: set[str] = set()

TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


@bp.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    #    print(request_data)
    subscribers_url.add(request_data["origin"])
    #    print(f"full set of subs {subscribers_url}")
    return "subscribed", 200


@bp.route("/<string:resource_id>/broadcast", methods=["POST"])
def broadcast(resource_id: str):
    data = request.get_json()
    requester_url: str = data["origin"]

    approvals: int = 0

    for url in subscribers_url:
        #        print(f"Asking {url} for {resource_id}")
        if url != requester_url:
            response = requests.get(
                f"{url}/{resource_id}/resource_status",
                json={},
                proxies=proxies,
                timeout=TIMEOUT,
            )

            #            print(f"after broadcast {r.text}, {r.status_code}")
            if response.status_code == 200:
                approvals += 1
    #         print(f"Registrar: received approval {resource_id} from {url}")

    if approvals == len(subscribers_url) - 1:
        return "resource free", 200

    return (
        f"""Does not obtain enough approval
        {approvals}/{len(subscribers_url) - 1}""",
        417,
    )

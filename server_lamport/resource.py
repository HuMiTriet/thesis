from dataclasses import dataclass
import os
import time
import threading
import json

import requests

from flask import Blueprint, request


TIMEOUT_SEC: int = 10

REQUEST_TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5004")

bp = Blueprint("resouce", __name__)


@dataclass
class ServerState:
    race_condition: bool = False


server_state = ServerState()


@bp.route("/race", methods=["GET"])
def check_race():

    if server_state.race_condition:
        return "race condition has occured", 423

    return "alles gut", 200


@bp.route("/<string:resource_id>", methods=["GET"])
def get(resource_id: str):
    with open(os.path.join("dummy_data.json"), "r", encoding="utf-8") as file:

        data = json.load(file)
        for item in data:
            if item["id"] == resource_id:
                return str(item), 200

    return "Resource not found", 404


def expire_lock(resource_id: str, duration: int, origin: str) -> None:
    time.sleep(duration)
    requests.delete(
        f"{origin}{resource_id}/lock",
        proxies={
            "http": PROXY_URL,
            "https": PROXY_URL,
        },
        timeout=REQUEST_TIMEOUT,
    )


# accquire a temporary lock on a resource that will expirce after 2s
@bp.route("/<string:resource_id>/lock", methods=["PUT"])
def lock(resource_id: str):
    # data = request.get_json()
    # origin = data["origin"]

    with open(os.path.join("dummy_data.json"), "r", encoding="utf-8") as file:

        data = json.load(file)
        for item in data:
            if item["id"] == resource_id:
                if item["is_locked"] is True:

                    server_state.race_condition = True
                    return (
                        f"Race condition: {resource_id} currently locked",
                        423,
                    )

                item["is_locked"] = True
                with open(
                    os.path.join("dummy_data.json"),
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(data, file)
                    # expire_thread = threading.Thread(
                    #     target=expire_lock,
                    #     args=(resource_id, TIMEOUT_SEC, origin),
                    # )
                    # expire_thread.start()
                    return "Success", 200

    return "Resource not found", 404


# explicitly release a lock on a resource
@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
def unlock(resource_id: str):
    with open(os.path.join("dummy_data.json"), "r", encoding="utf-8") as file:

        data = json.load(file)
        for item in data:
            if item["id"] == resource_id:
                # if item["is_locked"] is True:
                item["is_locked"] = False
                with open(
                    os.path.join("dummy_data.json"),
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(data, file)
                    return "Success", 200
                # else:
                # return "Resource not locked", 418

    return "Resource not found", 404


# replace resource with new data
@bp.route("/<string:resource_id>", methods=["PUT"])
def update(resource_id: str):
    with open(
        os.path.join("dummy_data.json"),
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)
        for item in data:
            if item["id"] == resource_id:
                if item["is_locked"] is True:
                    RACE_CONDITION = True
                    return "Resource currently locked", 423

                request_data = request.get_json()
                item["id"] = request_data["id"]
                locking_status = request_data["is_locked"]
                if locking_status is True:
                    item["is_locked"] = True
                    update_thread = threading.Thread(
                        target=expire_lock, args=(resource_id, TIMEOUT_SEC)
                    )
                    update_thread.start()
                with open(
                    os.path.join("dummy_data.json"),
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(data, file)

                    return "Success", 200

    return "Resource not found", 404

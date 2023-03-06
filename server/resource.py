from flask import Blueprint, request
import os
import time
import multiprocessing

TIMEOUT_SEC: int = 3

bp = Blueprint("resouce", __name__)


@bp.route("/<string:id>", methods=["GET"])
def get(id: str):
    with open(os.path.join("dummy_data.json"), "r") as f:
        import json

        data = json.load(f)
        for item in data:
            if item["id"] == id:
                return str(item), 200

    return "Resource not found", 404


def expire_lock(id: str, duration: int) -> None:
    with open(os.path.join("dummy_data.json"), "r") as f:
        import json

        time.sleep(duration)

        data = json.load(f)
        for item in data:
            if item["id"] == id:
                item["is_locked"] = False
                with open(
                    os.path.join("dummy_data.json"),
                    "w",
                ) as f:
                    json.dump(data, f)


# accquire a temporary lock on a resource that will expirce after 2s
@bp.route("/<string:id>/lock", methods=["PUT"])
def lock(id: str):
    with open(os.path.join("dummy_data.json"), "r") as f:
        import json

        data = json.load(f)
        for item in data:
            if item["id"] == id:
                if item["is_locked"] is True:
                    return "Resource currently locked", 423
                else:
                    item["is_locked"] = True
                    with open(
                        os.path.join("dummy_data.json"),
                        "w",
                    ) as f:
                        json.dump(data, f)
                        process = multiprocessing.Process(
                            target=expire_lock, args=(id, TIMEOUT_SEC)
                        )
                        process.start()
                        return "Success", 200

    return "Resource not found", 404


# explicitly release a lock on a resource
@bp.route("/<string:id>/lock", methods=["DELETE"])
def unlock(id: str):
    with open(os.path.join("dummy_data.json"), "r") as f:
        import json

        data = json.load(f)
        for item in data:
            if item["id"] == id:
                if item["is_locked"] is True:
                    item["is_locked"] = False
                    with open(
                        os.path.join("dummy_data.json"),
                        "w",
                    ) as f:
                        json.dump(data, f)
                        return "Success", 200
                else:
                    return "Resource not locked", 400

    return "Resource not found", 404


# replace resource with new data
@bp.route("/<string:id>", methods=["PUT"])
def update(id: str):
    with open(os.path.join("dummy_data.json"), "r") as f:
        import json

        data = json.load(f)
        for item in data:
            if item["id"] == id:
                if item["is_locked"] is True:
                    return "Resource currently locked", 423
                else:
                    request_data = request.get_json()
                    item["id"] = request_data["id"]
                    locking_status = request_data["is_locked"]
                    if locking_status is True:
                        item["is_locked"] = True
                        process = multiprocessing.Process(
                            target=expire_lock, args=(id, TIMEOUT_SEC)
                        )
                        process.start()
                    with open(
                        os.path.join("dummy_data.json"),
                        "w",
                    ) as f:
                        json.dump(data, f)

                        return "Success", 200

    return "Resource not found", 404

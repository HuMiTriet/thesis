from flask import Blueprint, request


bp = Blueprint("resource", __name__)


data = [
    {"id": 1, "name": "test1"},
    {"id": 2, "name": "test2"},
    {"id": 3, "name": "test3"},
]


# get the resource with that specific id
@bp.route("/<int:id>", methods=["GET"])
def get(id: int):
    return data[id - 1]


# update the resource
@bp.route("/<int:id>", methods=["PUT"])
def update(id: int):
    request_data = request.get_json()
    try:
        data[id - 1] = request_data
        return "Success", 200
    except IndexError:
        return "Resource not found", 404

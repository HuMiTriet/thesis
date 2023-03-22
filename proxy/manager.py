from flask import Blueprint
from requests import Response
from flask import request
from proxy.fault import ErrorFault, Fault

from proxy.fault import DelayFault


bp = Blueprint("manager", __name__)

faults: dict[str, Fault] = {}


@bp.route("/fault/<string:name>", methods=["POST"])
def fault_factory(name: str):
    data = request.get_json()
    condition = data["condition"]

    match data["type"]:
        case "delay":
            delayFault = DelayFault(
                condition=condition,
                duration=data["metadata"],
                name=data["name"],
            )

            faults[name] = delayFault

            return 'fault type "Delay" added', 200
        case "error":
            status_code = data["metadata"]["status_code"]
            text = data["metadata"]["text"]

            errorFault = ErrorFault(
                condition=condition,
                name=data["name"],
                text=text,
                status_code=status_code,
            )

            faults[name] = errorFault

            print(errorFault)
            return 'fault type "Error" added', 200
        case _:
            return f'fault type {data["type"]} unknown', 406


@bp.route("/fault/<string:name>", methods=["DELETE"])
def delete_fault(name: str):
    try:
        faults.pop(name)
        return "OK", 200
    except ValueError as e:
        return e.__repr__(), 416

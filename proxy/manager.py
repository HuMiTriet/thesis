from flask import Blueprint, json
from requests import Response
from flask import request
from proxy.fault import ErrorFault, Fault

from proxy.fault import DelayFault


bp = Blueprint("manager", __name__)

# faults: dict[str, Fault] = {}
# faults_currently_injected: list[str] = []


class ManagerState:
    faults: dict[str, Fault] = {}  # all posible faults
    faults_currently_injected: list[str] = []  # the fault we r currently using


managerState = ManagerState()


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

            managerState.faults[name] = delayFault

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

            managerState.faults[name] = errorFault

            print(errorFault)
            return 'fault type "Error" added', 200
        case _:
            return f'fault type {data["type"]} unknown', 406


@bp.route("/fault/<string:name>", methods=["DELETE"])
def delete_fault(name: str):
    try:
        managerState.faults.pop(name)
        return "OK", 200
    except ValueError as e:
        return e.__repr__(), 416


@bp.route("/inject", methods=["PATCH"])
def update_injections():
    try:
        data = request.get_json()

        managerState.faults_currently_injected = json.loads(data)

        # print(
        #     f"NEW manager injections {managerState.faults_currently_injected}"
        # )

        return "New injects loaded", 200
    except Exception as e:
        return e.__repr__(), 504


@bp.route("/inject", methods=["DELETE"])
def clear_injections():
    managerState.faults_currently_injected.clear()
    return "injections cleared", 200

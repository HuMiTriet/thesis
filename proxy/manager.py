import os
from dataclasses import dataclass, field
from flask import Blueprint
from flask import request
from proxy.fault import ErrorFault, Fault

from proxy.fault import DelayFault


bp = Blueprint("manager", __name__)

TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


@dataclass
class ManagerState:
    faults: dict[str, Fault] = field(
        default_factory=dict[str, Fault]
    )  # all of the possible faults
    faults_currently_injected: list[str] = field(
        default_factory=list[str]
    )  # the fault we r currently using


managerState = ManagerState()


@bp.route("/fault", methods=["POST"])
def fault_factory():
    data = request.get_json()
    condition = data["condition"]
    name = data["name"]

    match data["type"]:
        case "delay":
            delay_fault = DelayFault(
                condition=condition,
                duration=data["metadata"],
                name=data["name"],
            )

            managerState.faults[name] = delay_fault

            print(f"delay fault {delay_fault} added")

            return 'fault type "Delay" added', 200
        case "error":
            status_code = data["metadata"]["status_code"]
            text = data["metadata"]["text"]

            error_fault = ErrorFault(
                condition=condition,
                name=data["name"],
                text=text,
                status_code=status_code,
            )

            managerState.faults[name] = error_fault

            print(f"error fault {error_fault} added")

            return 'fault type "Error" added', 200
        case _:
            return f'fault type {data["type"]} unknown', 406


@bp.route("/fault/<string:name>", methods=["DELETE"])
def delete_fault(name: str):
    try:
        managerState.faults.pop(name)
        return "OK", 200
    except ValueError as error:
        return str(error.__repr__), 416


@bp.route("/inject", methods=["POST"])
def update_injections():
    try:
        data = request.get_json()

        managerState.faults_currently_injected = data["fault"]

        print(
            f"currently now using {managerState.faults_currently_injected} with full {managerState.faults}"
        )

        return f"New injects {data} loaded", 200

    except Exception as error:  # pylint: disable=broad-exception-caught
        return str(error.__repr__), 504


# @bp.route("/inject", methods=["POST"])
# def append_injections():
#     try:
#         data = request.get_json()

#         print(f"appending {data}")
#         managerState.faults_currently_injected.append(data["fault_name"])

#         return f"New injects {data} loaded", 200
#     except Exception as e:
#         return e.__repr__(), 504


@bp.route("/is_alive", methods=["GET"])
def is_alive():
    return "yes", 200


@bp.route("/inject", methods=["DELETE"])
def clear_injections():
    managerState.faults_currently_injected.clear()
    return "injections cleared", 200

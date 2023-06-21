import os
from dataclasses import dataclass, field
from flask import Blueprint
from flask import request
from proxy.fault import ErrorFault, Fault

from proxy.fault import DelayFault


bp = Blueprint("manager", __name__)


@dataclass
class ManagerState:
    faults: dict[str, Fault] = field(
        default_factory=dict[str, Fault]
    )  # all of the possible faults
    faults_currently_injected: list[str] = field(
        default_factory=list[str]
    )  # the fault we r currently using


managerState = ManagerState()

for i in range(0, 21):
    duration = i / 100
    managerState.faults[str(duration)] = DelayFault(
        condition="True",
        duration=duration,
        name=str(duration),
    )


@bp.route("/fault", methods=["POST"])
def fault_factory():
    all_data = request.get_json()
    for data in all_data:
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

                # return 'fault type "Delay" added', 200
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

                # return 'fault type "Error" added', 200
            case _:
                return f'fault type {data["type"]} unknown', 406
    return "ok", 200

    # condition = data["condition"]
    # name = data["name"]


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
        return f"New injects {data} loaded", 200

    except Exception as error:
        return str(error.__repr__), 504


@bp.route("/is_alive", methods=["GET"])
def is_alive():
    return str(managerState.faults.keys()), 200


@bp.route("/inject", methods=["DELETE"])
def clear_injections():
    managerState.faults_currently_injected.clear()
    return "injections cleared", 200

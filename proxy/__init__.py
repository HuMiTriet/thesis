import typing
from flask import Flask, request
import requests
from requests import Response
import random

from .fault import ErrorFault

from .manager import managerState

proxies = {
    "http": "http://127.0.0.1:5004",
    "https": "http://127.0.0.1:5004",
}


def create_app():

    app = Flask(__name__)

    @app.route(
        "/<path:url>",
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    def handler(url: str):

        response: Response = Response()

        # randomly chooses a fault and runs it
        # print(f"FAULT LEN {len(faults)}")
        if len(managerState.faults) != 0:
            # print(managerState.faults_currently_injected)
            for fault in managerState.faults_currently_injected:
                choosen_fault = managerState.faults[fault]
                # print(f"Fault that will be executed {choosen_fault}")
                if isinstance(choosen_fault, ErrorFault):
                    # typing.cast(ErrorFault, choosen_fault)
                    res = choosen_fault.execute(request=request, url=url)
                    if res is not None:
                        return res
                else:
                    choosen_fault.execute(request=request, url=url)

        match request.method:
            case "GET":
                response = requests.get(f"{request.url}", json=request.json)
            case "POST":
                response = requests.post(f"{request.url}", json=request.json)
            case "PUT":
                response = requests.put(f"{request.url}", json=request.json)
            case "DELETE":
                response = requests.delete(f"{request.url}")

        return response.text, response.status_code

    from . import manager

    app.register_blueprint(manager.bp)

    return app

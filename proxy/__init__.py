import os
from dotenv import load_dotenv
from flask import Flask, request
import requests
from requests import Response
from werkzeug.exceptions import InternalServerError
import re


from .fault import ErrorFault


from .manager import managerState

TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))


def create_app():

    load_dotenv()

    app = Flask(__name__)

    @app.route(
        "/<path:url>",
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    def handler(url: str):  # pyright: ignore

        response: Response = Response()

        if len(managerState.faults) != 0:
            for fault in managerState.faults_currently_injected:

                choosen_fault = managerState.faults[fault]

                print(f"1 url {url} choosen_fault: {choosen_fault}")

                if isinstance(choosen_fault, ErrorFault):
                    res = choosen_fault.execute(request=request, url=url)
                    if res is not None:
                        return res
                else:
                    choosen_fault.execute(request=request, url=url)

        match request.method:
            case "GET":
                response = requests.get(
                    f"{request.url}",
                    json=request.json,
                    timeout=TIMEOUT,
                )
            case "POST":
                response = requests.post(
                    f"{request.url}",
                    json=request.json,
                    timeout=TIMEOUT,
                )
            case "PUT":
                # match = re.findall("http://127.0.0.1:5000/./lock", url)
                # if len(match) != 0:
                print(
                    f"client {request.get_json()['origin']} is locking {url}"
                )

                response = requests.put(
                    f"{request.url}",
                    json=request.json,
                    timeout=TIMEOUT,
                )
            case "DELETE":
                response = requests.delete(
                    f"{request.url}",
                    timeout=TIMEOUT,
                )

        return response.text, response.status_code

    @app.errorhandler(InternalServerError)
    def custom_error_msg(error: InternalServerError):  # pyright: ignore
        return f"PROXY Err {error.__repr__}", 500

    # pylint: disable=import-outside-toplevel
    from . import manager

    app.register_blueprint(manager.bp)

    return app

from flask import Flask, request
import requests
from requests import Response
import random

from .manager import faults


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
        if len(faults) != 0:
            random.choice(list(faults.values())).execute(
                request=request, url=url
            )

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

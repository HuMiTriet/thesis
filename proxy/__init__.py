import os
from flask import Flask, request
import requests
from requests import Response


proxies = {
    "http": "http://127.0.0.1:5004",
    "https": "http://127.0.0.1:5004",
}


def create_app():

    app = Flask(__name__)

    # session = requests.Session()
    # session.proxies.update(proxies)

    @app.route(
        "/<path:url>",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "UPDATE"],
    )
    def handler(url):
        response: Response = Response()

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

    return app

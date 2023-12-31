import os
import aiohttp
from dotenv import load_dotenv
from flask import Flask, request
import requests
from requests import Response
from werkzeug.exceptions import InternalServerError


from .fault import ErrorFault


from .manager import managerState


def create_app():
    load_dotenv()

    app = Flask(__name__)

    @app.route(
        "/<path:url>",
        methods=["GET", "POST", "PUT", "DELETE"],
    )
    async def handler(url: str):  # pyright: ignore
        delay_time = request.get_json()["delay_time"]

        if len(managerState.faults) != 0:
            # for fault in managerState.faults_currently_injected:
            choosen_fault = managerState.faults[delay_time]

            if isinstance(choosen_fault, ErrorFault):
                res = await choosen_fault.execute(request=request, url=url)
                if res is not None:
                    return res
            else:
                await choosen_fault.execute(request=request, url=url)

        async with aiohttp.ClientSession() as session:
            match request.method:
                case "GET":
                    async with session.get(
                        f"{request.url}",
                        json=request.json,
                    ) as res:
                        return await res.text(), res.status
                case "POST":
                    async with session.post(
                        f"{request.url}",
                        json=request.json,
                    ) as res:
                        return await res.text(), res.status
                case "PUT":
                    async with session.put(
                        f"{request.url}",
                        json=request.json,
                    ) as res:
                        return await res.text(), res.status
                case "DELETE":
                    async with session.delete(
                        f"{request.url}",
                        json=request.json,
                    ) as res:
                        return await res.text(), res.status

        return "failed", 423

    @app.errorhandler(InternalServerError)
    def custom_error_msg(error: InternalServerError):  # pyright: ignore
        return f"PROXY Err {error.__repr__}", 500

    # pylint: disable=import-outside-toplevel
    from . import manager

    app.register_blueprint(manager.bp)

    return app

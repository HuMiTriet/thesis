import os
import asyncio

from flask import Blueprint, request
import aiohttp


from . import client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

CLIENT_URL: str = os.getenv("CLIENT_URL", "http://127.0.0.1:5004")

TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")

bp = Blueprint("gossip", __name__)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:

    if resource_id in client_state.currently_using_resource_id:
        return (
            f"resource {resource_id} is already executing by {request.host_url}",
            200,
        )

    broadcast_urls = client_state.get_quorum_urls(request.host_url)

    async with aiohttp.ClientSession() as session:

        coroutines = []

        for target_url in broadcast_urls:
            coroutine = session.post(
                f"{target_url}{resource_id}/resource_status",
                json={
                    "origin": request.host_url,
                },
                proxy=PROXY_URL,
            )
            coroutines.append(coroutine)

        await asyncio.gather(*coroutines)

    return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):
    print(
        f"client {request.host_url} being asked {resource_id} by {request.get_json()['origin']}"
    )

    return "foobar", 200


# @bp.route("/<string:resource_id>/reply", methods=["POST"])
# async def receive_reply(resource_id: str):

import os
import asyncio

from flask import Blueprint, request
import aiohttp


from . import ClientRequest, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

CLIENT_URL: str = os.getenv("CLIENT_URL", "http://127.0.0.1:5004")

TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")

bp = Blueprint("gossip", __name__)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:

    if not client_state.queued_request.empty():
        if client_state.queued_request.queue[0] == ClientRequest(
            url=request.host_url,
            resource_id=resource_id,
        ):
            return (
                f"resource {resource_id} is already executing by {request.host_url}",
                200,
            )

    client_state.queued_request.put(
        ClientRequest(
            url=request.host_url,
            resource_id=resource_id,
        )
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
                timeout=TIMEOUT,
            )
            coroutines.append(coroutine)

        await asyncio.gather(*coroutines)

    return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):

    original_url = request.get_json()["origin"]

    received_request = ClientRequest(
        url=original_url,
        resource_id=resource_id,
    )

    client_state.queued_request.put(received_request)

    if client_state.queued_request.queue[0] == received_request:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                f"{original_url}{resource_id}/reply",
                json={
                    "approve_url": original_url,
                },
                timeout=TIMEOUT,
            ):
                return (
                    f"""client {request.host_url} grant client {original_url}
                    access of {resource_id}""",
                    200,
                )

    return (
        f"client {request.host_url} does not grant client {original_url} access of {resource_id}",
        420,
    )


@bp.route("/<string:resource_id>/reply", methods=["POST"])
async def receive_reply(resource_id: str):

    data = request.get_json()

    approve_url = data["approve_url"]

    received_request = ClientRequest(
        url=approve_url,
        resource_id=resource_id,
    )

    for i in range(client_state.queued_request.qsize()):
        current_request = client_state.queued_request.queue[i]
        print(f"current {current_request} and recv {received_request}")
        if current_request == received_request:
            current_request.approvals += 1

            if current_request.approvals == (
                len(client_state.quorum_urls) - 1
            ):
                await lock_resource(resource_id)
                return f"Client locked {resource_id}", 200

    return "client did not receive enough approval", 420


async def lock_resource(resource_id: str) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{SERVER_URL}{resource_id}/lock",
            json={},
            proxy=PROXY_URL,
        ) as response:
            return await response.text(), response.status


@bp.route("/<string:resource_id>/delete", methods=["DELETE"])
async def delete_request(resource_id: str):
    pass

import os
import asyncio

# from datetime import datetime
from flask import Blueprint, request
import aiohttp
from time import time


from . import ClientRequest, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

CLIENT_URL: str = os.getenv("CLIENT_URL", "http://127.0.0.1:5004")

TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")

LOGGER_URL: str = os.getenv("LOGGER_URL", "http://127.0.0.1:3000/")

bp = Blueprint("gossip", __name__)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:
    # resource_queue = client_state.get_request_queue(resource_id)

    # if not client_state.get_resource_queue(resource_id).count:
    if len(client_state.get_request_queue(resource_id)) != 0:

        if client_state.get_request_queue(resource_id)[0].approvals == len(
            client_state.get_broadcast_urls(request.host_url)
        ):
            return f"client {request.host_url} is executing", 200

    if (
        len(client_state.get_request_queue(resource_id)) == 0
        or client_state.get_request_queue(resource_id)[0].url
        != request.host_url
    ):
        client_state.get_request_queue(resource_id).append(
            ClientRequest(
                url=request.host_url,
                approvals=0,
            )
        )

    # print(
    #     f"we are going to compare {resource_queue[0].url} and {request.host_url}"
    # )

    # print(
    #     f"client current queue {[resource.url for resource in resource_queue]}"
    # )

    broadcast_urls = client_state.get_broadcast_urls(request.host_url)

    async with aiohttp.ClientSession() as session:

        coroutines = []

        coroutines.append(
            session.put(
                f"{LOGGER_URL}{resource_id}/log",
                json={
                    "type": "start",
                    "client_url": request.host_url,
                    "time": time(),
                },
                timeout=TIMEOUT,
            )
        )

        for target_url in set(broadcast_urls).difference(
            client_state.get_request_queue(resource_id)[
                0
            ].already_given_approvals
        ):
            coroutine = session.post(
                f"{target_url}{resource_id}/resource_status",
                json={
                    "origin": request.host_url,
                },
                proxy=PROXY_URL,
                timeout=TIMEOUT,
            )
            coroutines.append(coroutine)

        try:
            await asyncio.wait_for(
                asyncio.gather(*coroutines), timeout=TIMEOUT
            )
        except asyncio.TimeoutError:
            # Handle the timeout, e.g., by aborting the request and trying again later
            client_state.get_request_queue(resource_id).pop(0)
            return "Request timed out. Please retry later.", 408

    return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):

    original_url = request.get_json()["origin"]

    client_state.get_request_queue(resource_id).append(
        ClientRequest(
            url=original_url,
        )
    )

    if client_state.get_request_queue(resource_id)[0].url == original_url:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                f"{original_url}{resource_id}/reply",
                json={
                    "approve_url": original_url,
                    "origin": request.host_url,
                },
                proxy=PROXY_URL,
                timeout=TIMEOUT,
            ):
                return (
                    f"""client {request.host_url} grant client {original_url}
                    access of {resource_id}""",
                    200,
                )

    return (
        f"client {request.host_url} does not grant client {original_url} access of {resource_id}",
        403,
    )


@bp.route("/<string:resource_id>/reply", methods=["POST"])
async def receive_reply(resource_id: str):

    data = request.get_json()

    approve_url = data["approve_url"]
    approver_url = data["origin"]

    for i in range(len(client_state.get_request_queue(resource_id))):
        current_request: ClientRequest = client_state.get_request_queue(
            resource_id
        )[i]
        # print(f"current {current_request} and recv {received_request}")
        if current_request.url == approve_url:
            # if datetime.now() >= current_request.expiration_time:
            #     # Request has expired, remove it from the queue and handle the expiration
            #     client_state.get_request_queue(resource_id).pop(i)
            #     return "Request expired.", 410

            current_request.approvals += 1
            current_request.already_given_approvals.add(approver_url)

            if (
                current_request.approvals
                == (len(client_state.get_broadcast_urls(request.host_url)))
                and client_state.get_request_queue(resource_id)[0].url
                == request.host_url
            ):

                # print(f"HERE CLIENT locking {resource_id}")
                await lock_resource(resource_id)
                return f"Client locked {resource_id}", 200

    return "client did not receive enough approval", 403


async def lock_resource(resource_id: str) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "origin": request.host_url,
            },
            proxy=PROXY_URL,
        ) as response:
            return await response.text(), response.status


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def delete_request(resource_id: str):

    # resource_queue = client_state.get_request_queue(resource_id)

    if (
        len(client_state.get_request_queue(resource_id)) != 0
        and client_state.get_request_queue(resource_id)[0].url
        == request.host_url
    ):
        current_request = client_state.get_request_queue(resource_id)[0]
        client_state.get_request_queue(resource_id).pop(0)

        broadcast_urls = client_state.get_broadcast_urls(request.host_url)

        async with aiohttp.ClientSession() as session:
            coroutines = []

            # delete the resource on server
            server_delete_coroutine = session.delete(
                f"{SERVER_URL}{resource_id}/lock",
                json={
                    "origin": current_request.url,
                },
                proxy=PROXY_URL,
                timeout=TIMEOUT,
            )

            coroutines.append(server_delete_coroutine)

            for target_url in broadcast_urls:
                coroutine = session.post(
                    f"{target_url}{resource_id}/release",
                    json={
                        "origin": current_request.url,
                    },
                    proxy=PROXY_URL,
                    timeout=TIMEOUT,
                )
                coroutines.append(coroutine)

            await asyncio.gather(*coroutines)

        message = f"""Client {current_request.url} has left the critical
        section for resource {resource_id}"""
        status = 200

    else:
        message = f"No request found for resource {resource_id}"
        status = 404

    return message, status


@bp.route("/<string:resource_id>/release", methods=["POST"])
async def release_resource(resource_id: str):
    # Parse the request to get the URL of the client that released the resource
    original_url = request.get_json()["origin"]

    # Get the resource queue for the specified resource_id
    # resource_queue = client_state.get_request_queue(resource_id)

    # Check if the resource queue is not empty
    if len(client_state.get_request_queue(resource_id)) != 0:
        # Remove the first request from the queue if it matches the original_url
        if client_state.get_request_queue(resource_id)[0].url == original_url:
            client_state.get_request_queue(resource_id).pop(0)

        # Check if the current process's request is now at the front of the queue
        if (
            len(client_state.get_request_queue(resource_id)) != 0
            and client_state.get_request_queue(resource_id)[0].url
            == request.host_url
        ):

            if client_state.get_request_queue(resource_id)[0].approvals == len(
                client_state.get_broadcast_urls(request.host_url)
            ):
                # print(f"HERE CLIENT locking {resource_id}")
                resp, status = await lock_resource(resource_id)
                return resp, status

            # Try to acquire the resource again
            # (e.g., by sending a request to the /request endpoint)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{request.host_url}{resource_id}/request",
                    json={},
                    proxy=PROXY_URL,
                    timeout=TIMEOUT,
                ):
                    pass

    return (
        f"Received release message from client {original_url} for resource {resource_id}",
        200,
    )

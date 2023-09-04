import logging
import os
import asyncio
from time import time

from flask import Blueprint, request

import aiohttp
import requests

from . import ResourceState, State, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

CLIENT_URL: str = os.getenv(
    "CLIENT_URL",
    "http://127.0.0.1:5002/ http://127.0.0.1:5003/ http://127.0.0.1:5004/ http://127.0.0.1:5005/",
)
TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")
LOGGER_URL: str = os.getenv("LOGGER_URL", "http://127.0.0.1:3000/")

bp = Blueprint("gossip", __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:
    data = request.get_json()
    delay_time: str = data["delay_time"]
    client_no: str = data["client_no"]

    if resource_id in client_state.resource_states.keys():
        return (
            f"resource {resource_id} is already executing by {request.host_url}",
            200,
        )

    requests.put(
        f"{LOGGER_URL}{resource_id}/log",
        json={
            "type": "start",
            "client_url": request.host_url,
            "time": time(),
            "delay_time": delay_time,
            "client_no": client_no,
        },
        timeout=TIMEOUT,
    )

    async with aiohttp.ClientSession() as session:
        client_state.resource_states[resource_id] = ResourceState(
            current_state=State.REQUESTING,
            approvals=0,
        )
        coroutines = []

        for target_url in CLIENT_URL.split():
            if target_url != request.host_url:
                coroutine = session.post(
                    f"{target_url}{resource_id}/resource_status",
                    json={
                        "origin": request.host_url,
                        "timestamp": client_state.lamport_clock.get_time(),
                        "delay_time": delay_time,
                        "client_no": client_no,
                    },
                    proxy=PROXY_URL,
                )
                coroutines.append(coroutine)

        await asyncio.gather(*coroutines)

        client_state.lamport_clock.increment()

        return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):
    async with aiohttp.ClientSession() as session:
        data = request.get_json()
        timestamp = data["timestamp"]
        origin = data["origin"]
        client_no: str = data["client_no"]
        delay_time: str = data["delay_time"]

        client_state.lamport_clock.update(timestamp)

        try:
            interested_resource: ResourceState = client_state.resource_states[
                resource_id
            ]
        except KeyError:
            async with session.post(
                f"{origin}/{resource_id}/reply",
                json={
                    "origin": request.host_url,
                    "timestamp": client_state.lamport_clock.get_time(),
                    "delay_time": delay_time,
                    "client_no": client_no,
                },
                proxy=PROXY_URL,
            ) as response:
                return (
                    f"client {request.host_url} is not req or exe {resource_id}",
                    200,
                )

        if interested_resource.current_state == State.REQUESTING:
            if client_state.lamport_clock.get_time() < timestamp:
                async with session.post(
                    f"{origin}/{resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": client_state.lamport_clock.get_time(),
                        "delay_time": delay_time,
                        "client_no": client_no,
                    },
                    proxy=PROXY_URL,
                ) as response:
                    return await response.text(), response.status

            client_state.deffered_replies.append(
                {"url": origin, "resource_id": resource_id}
            )
            return "request deffered", 420

        if interested_resource.current_state == State.EXECUTING:
            client_state.deffered_replies.append(
                {"url": origin, "resource_id": resource_id}
            )
            return "request deffered", 420

        async with session.post(
            f"{origin}/{resource_id}/reply",
            json={
                "origin": request.host_url,
                "timestamp": client_state.lamport_clock.get_time(),
                "delay_time": delay_time,
                "client_no": client_no,
            },
            proxy=PROXY_URL,
        ) as response:
            return await response.text(), response.status


@bp.route("/<string:resource_id>/reply", methods=["POST"])
async def receive_reply(resource_id: str):
    # print(
    #     f"""{request.host_url} getting a reply from {request.get_json()['origin']}
    #     for {resource_id}
    #     """
    # )

    try:
        interested_resource: ResourceState = client_state.resource_states[
            resource_id
        ]
    except KeyError as error:
        # print(
        #     f"client {request.host_url} does not have {resource_id} {client_state.resource_states}"
        # )
        return (
            f"client does not have {resource_id} in resource_states {repr(error)}",
            412,
        )

    interested_resource.approvals += 1

    data = request.get_json()

    timestamp = data["timestamp"]
    delay_time = data["delay_time"]
    client_no: str = data["client_no"]
    client_state.lamport_clock.update(timestamp)

    # await asyncio.sleep(0.01)

    if interested_resource.approvals == int(TOTAL_CLIENT) - 1:
        interested_resource.approvals = 0
        interested_resource.current_state = State.EXECUTING

        text, code = await lock_resource(resource_id, delay_time, client_no)

        return text, code

    return (
        f"""couldn't lock {resource_id} bc approvals of {request.host_url}:
        {interested_resource.approvals}""",
        420,
    )


async def lock_resource(
    resource_id: str, delay_time: str, client_no: str
) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        # print(f"client {request.host_url} put lock on {resource_id}")
        async with session.put(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "origin": request.host_url,
                "timestamp": client_state.lamport_clock.get_time(),
                "delay_time": delay_time,
                "client_no": client_no,
            },
            proxy=PROXY_URL,
        ) as response:
            client_state.lamport_clock.increment()
            return await response.text(), response.status


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def revoke_lock(resource_id: str):
    # print(
    #     f"client  at {request.host_url} with {request.get_json()['client_no']}"
    # )
    if client_state.resource_states.get(resource_id) is None:
        return "resource not held", 200

    if (
        client_state.resource_states[resource_id].current_state
        != State.EXECUTING
    ):
        return "resource held but not executing", 200

    data = request.get_json()
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "type": "end",
                "client_url": request.host_url,
                "time": time(),
                "delay_time": data["delay_time"],
                "client_no": data["client_no"],
            },
            proxy=PROXY_URL,
        ) as response:
            client_state.lamport_clock.increment()
            client_state.resource_states.pop(resource_id)

        # send reply to all deffered_replies
        for deffered in client_state.deffered_replies:
            deffered_resource_id = deffered["resource_id"]
            if deffered_resource_id == resource_id:
                url = deffered["url"]

                async with session.post(
                    f"{url}{deffered_resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": client_state.lamport_clock.get_time(),
                        "delay_time": request.get_json()["delay_time"],
                        "client_no": request.get_json()["client_no"],
                    },
                    proxy=PROXY_URL,
                ) as response:
                    return await response.text(), response.status

    return f"revoked resource {resource_id}", 200

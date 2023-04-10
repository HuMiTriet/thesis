import asyncio
import logging
import os
from flask import Blueprint, request
import requests
import aiohttp

from . import ResourceState, State, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5004")

bp = Blueprint("gossip", __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@bp.route("/register", methods=["POST"])
def register():
    """
    This is used in the registrar version. Each client register to the
    registrar
    """
    client_state.lamport_clock.increment()

    response = requests.post(
        f"{REGISTRAR_URL}/register",
        json={"origin": request.host_url},
        proxies={
            "http": PROXY_URL,
            "https": PROXY_URL,
        },
        timeout=TIMEOUT,
    )

    return response.text, response.status_code


# @bp.route("/<string:resource_id>/lock", methods=["POST"])
# async def lock(resource_id: str) -> tuple[str, int]:

#     state.requesting_resource.add(resource_id)
#     state.lamport_clock.increment()

#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(
#                 f"{REGISTRAR_URL}/{resource_id}/broadcast",
#                 json={
#                     "origin": request.host_url,
#                     "timestamp": state.lamport_clock.get_time(),
#                 },
#                 proxy=PROXY_URL,
#                 timeout=TIMEOUT,
#             ) as response:

#                 if response.status == 200:

#                     state.lamport_clock.increment()
#                     lock_resource(resource_id, request.host_url)

#                     return (
#                         f"""resource {resource_id} is being
#                         locked by {request.host_url}""",
#                         200,
#                     )

#     except asyncio.exceptions.TimeoutError as error:
#         return str(error.__repr__), 403

#     state.requesting_resource.remove(resource_id)
#     state.lamport_clock.increment()
#     return await response.text(), 401


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:

    if resource_id in client_state.resource_states.keys():
        return (
            f"resource {resource_id} is already executing by {request.host_url}",
            200,
        )

    async with aiohttp.ClientSession() as session:

        target_url = "http://127.0.0.1:5002/"
        if request.host_url == target_url:
            target_url = "http://127.0.0.1:5003/"

        client_state.resource_states[resource_id] = ResourceState(
            current_state=State.REQUESTING,
            approvals=0,
        )

        async with session.post(
            f"{target_url}{resource_id}/resource_status",
            json={
                "origin": request.host_url,
                "timestamp": client_state.lamport_clock.get_time(),
            },
            proxy=PROXY_URL,
        ):

            client_state.lamport_clock.increment()

        return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):
    async with aiohttp.ClientSession() as session:

        data = request.get_json()
        timestamp = data["timestamp"]
        origin = data["origin"]

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
                },
            ) as response:
                return (
                    f"client {request.host_url} is not req or exe {resource_id}",
                    200,
                )

        # if (
        #     client_state.current_state == ClientState.REQUESTING
        #     and resource_id in client_state.requesting_resource
        # ):
        if interested_resource.current_state == State.REQUESTING:
            if client_state.lamport_clock.get_time() < timestamp:
                async with session.post(
                    f"{origin}/{resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": client_state.lamport_clock.get_time(),
                    },
                ) as response:
                    return await response.text(), response.status

            client_state.deffered_replies.append(
                {"url": origin, "resource_id": resource_id}
            )
            return "request deffered", 420

        # if (
        #     client_state.current_state == ClientState.EXECUTING
        #     and resource_id in client_state.executing_resource
        # ):
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
            },
        ) as response:
            return await response.text(), response.status


@bp.route("/<string:resource_id>/reply", methods=["POST"])
async def receive_reply(resource_id: str):
    async with aiohttp.ClientSession() as session:

        print(
            f"{request.host_url} getting a reply from {request.get_json()['origin']} for {resource_id}"
        )

        try:
            interested_resource: ResourceState = client_state.resource_states[
                resource_id
            ]
        except KeyError as error:
            print(
                f"client {request.host_url} does not have {resource_id} {client_state.resource_states}"
            )
            return (
                f"client does not have {resource_id} in resource_states {repr(error)}",
                412,
            )

        interested_resource.approvals += 1

        data = request.get_json()

        timestamp = data["timestamp"]
        client_state.lamport_clock.update(timestamp)

        await asyncio.sleep(0.1)

        # if (
        #     interested_resource.approvals[resource_id] == 1
        #     and resource_id in client_state.requesting_resource
        # ):
        if interested_resource.approvals == 1:

            interested_resource.approvals = 0
            interested_resource.current_state = State.EXECUTING

            print(f"client {request.host_url} put lock on {resource_id}")
            async with session.put(
                f"{SERVER_URL}{resource_id}/lock",
                json={
                    "origin": request.host_url,
                    "timestamp": client_state.lamport_clock.get_time(),
                },
                proxy=PROXY_URL,
            ) as response:
                client_state.lamport_clock.increment()
                return await response.text(), response.status

        return (
            f"""couldn't lock {resource_id} bc approvals of {request.host_url}:
            {interested_resource.approvals}""",
            420,
        )


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def revoke_lock(resource_id: str):
    async with aiohttp.ClientSession() as session:

        async with session.delete(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "origin": request.host_url,
                "timestamp": client_state.lamport_clock.get_time(),
            },
            proxy=PROXY_URL,
        ) as response:
            client_state.lamport_clock.increment()

            # client_state.current_state = ClientState.DEFAULT
            # client_state.executing_resource.discard(resource_id)
            # client_state.requesting_resource.discard(resource_id)
            # client_state.approvals[resource_id] = 0

            client_state.resource_states.pop(resource_id)

            # send reply to all deffered_replies

            for deffered in client_state.deffered_replies:
                url = deffered["url"]
                deffered_resource_id = deffered["resource_id"]

                async with session.post(
                    f"{url}{deffered_resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": client_state.lamport_clock.get_time(),
                    },
                    proxy=PROXY_URL,
                ) as response:
                    return await response.text(), response.status

    return f"revoked resource {resource_id}", 200

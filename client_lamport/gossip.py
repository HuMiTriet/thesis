import asyncio
import logging
import os
from flask import Blueprint, request
import requests
import aiohttp

from . import ClientState, state


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
    state.lamport_clock.increment()

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
    async with aiohttp.ClientSession() as session:

        target_url = "http://127.0.0.1:5002/"
        if request.host_url == target_url:
            target_url = "http://127.0.0.1:5003/"

        async with session.post(
            f"{target_url}{resource_id}/resource_status",
            json={
                "origin": request.host_url,
                "timestamp": state.lamport_clock.get_time(),
            },
            proxy=PROXY_URL,
            # timeout=TIMEOUT,
        ):
            state.current_state = ClientState.REQUESTING
            state.requesting_resource.add(resource_id)
            state.approvals[resource_id] = 0
            state.lamport_clock.increment()
        return f"client {request.host_url} is requesting {resource_id}", 200


@bp.route("/<string:resource_id>/resource_status", methods=["POST"])
async def resource_status(resource_id: str):
    async with aiohttp.ClientSession() as session:

        data = request.get_json()
        timestamp = data["timestamp"]
        origin = data["origin"]

        state.lamport_clock.update(timestamp)

        if (
            state.current_state == ClientState.REQUESTING
            and resource_id in state.requesting_resource
        ):
            if state.lamport_clock.get_time() < timestamp:
                async with session.post(
                    f"{origin}/{resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": state.lamport_clock.get_time(),
                    },
                ) as response:
                    return await response.text(), response.status

            state.deffered_replies.append(
                {"url": origin, "resource_id": resource_id}
            )
            return "request deffered", 420

        if (
            state.current_state == ClientState.EXECUTING
            and resource_id in state.executing_resource
        ):
            state.deffered_replies.append(
                {"url": origin, "resource_id": resource_id}
            )
            return "request deffered", 420

        async with session.post(
            f"{origin}/{resource_id}/reply",
            json={
                "origin": request.host_url,
                "timestamp": state.lamport_clock.get_time(),
            },
        ) as response:
            return await response.text(), response.status


@bp.route("/<string:resource_id>/reply", methods=["POST"])
async def receive_reply(resource_id: str):
    async with aiohttp.ClientSession() as session:

        state.approvals[resource_id] = state.approvals.get(resource_id, 0) + 1

        data = request.get_json()

        timestamp = data["timestamp"]
        state.lamport_clock.update(timestamp)

        await asyncio.sleep(0.1)
        print(
            f"HERE client {request.host_url} has state approvals {state.approvals[resource_id]}"
        )

        if state.approvals[resource_id] == 1:
            state.approvals[resource_id] = 0
            state.current_state = ClientState.EXECUTING
            print(
                f"client {request.host_url} trying to remove {state.requesting_resource}"
            )
            state.requesting_resource.discard(resource_id)
            state.executing_resource.add(resource_id)

            async with session.put(
                f"{SERVER_URL}{resource_id}/lock",
                json={
                    "origin": request.host_url,
                    "timestamp": state.lamport_clock.get_time(),
                },
                proxy=PROXY_URL,
            ) as response:
                state.lamport_clock.increment()
                return await response.text(), response.status

        return (
            f"couldn't lock {resource_id} bc replies {state.approvals[resource_id]}",
            420,
        )


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def revoke_lock(resource_id: str):
    async with aiohttp.ClientSession() as session:

        # increment

        async with session.delete(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "origin": request.host_url,
                "timestamp": state.lamport_clock.get_time(),
            },
            proxy=PROXY_URL,
        ) as response:
            state.lamport_clock.increment()

            state.current_state = ClientState.DEFAULT
            state.executing_resource.discard(resource_id)
            state.requesting_resource.discard(resource_id)
            state.approvals[resource_id] = 0

            # send reply to all deffered_replies

            for deffered in state.deffered_replies:
                url = deffered["url"]
                deffered_resource_id = deffered["resource_id"]

                async with session.post(
                    f"{url}{deffered_resource_id}/reply",
                    json={
                        "origin": request.host_url,
                        "timestamp": state.lamport_clock.get_time(),
                    },
                    proxy=PROXY_URL,
                ) as response:
                    return await response.text(), response.status

    return f"revoked resource {resource_id}", 200

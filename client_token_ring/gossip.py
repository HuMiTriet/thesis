import asyncio
import os

# from datetime import datetime
from flask import Blueprint, request
import aiohttp


from . import State, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")

CLIENT_URL: str = os.getenv("CLIENT_URL", "http://127.0.0.1:5004")

TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")

bp = Blueprint("gossip", __name__)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:

    if client_state.current_state[resource_id] == State.EXECUTING:
        return f"client is already executing resource {resource_id}", 200

    if client_state.current_state[resource_id] == State.DEFAULT:
        client_state.current_state[resource_id] = State.REQUESTING

    return f"client has requested {resource_id}", 200


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def delete_request(resource_id: str) -> tuple[str, int]:

    if client_state.current_state[resource_id] == State.DEFAULT:
        return (
            f"client cannot delete {resource_id} lock because has not yet hold it",
            401,
        )

    if client_state.current_state[resource_id] == State.EXECUTING:
        client_state.current_state[resource_id] = State.DEFAULT
        await asyncio.gather(
            release_lock(resource_id),
            pass_token(resource_id),
        )
        return f"client release token {resource_id} and passed it along", 200

    return f"client REQUESTING {resource_id} to DEFAULT)", 200


@bp.route("/<string:resource_id>/token", methods=["PUT"])
async def receive_token(resource_id: str) -> tuple[str, int]:

    if client_state.current_state[resource_id] == State.DEFAULT:
        resp, code = await pass_token(resource_id)
        return resp, code

    if client_state.current_state[resource_id] == State.REQUESTING:
        client_state.current_state[resource_id] = State.EXECUTING
        # print(f"client {request.host_url} is locking {resource_id}")
        resp, code = await lock_resource(resource_id)
        return resp, code

    # The only state remaining is EXECUTING but if the client is executing then
    # it is currently holding that token so it can't receive a token from somewhere else
    return f"duplication of token for {resource_id}", 400


async def pass_token(resource_id: str) -> tuple[str, int]:
    next_url = client_state.get_next_client_url(request.host_url)
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{next_url}{resource_id}/token") as response:
            return (
                f"client has passed token {resource_id} to {next_url}",
                response.status,
            )


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


async def release_lock(resource_id: str) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{SERVER_URL}{resource_id}/lock",
            json={},
            proxy=PROXY_URL,
            timeout=TIMEOUT,
        ) as response:
            return await response.text(), response.status

import asyncio
import os
import threading
from time import time


# from datetime import datetime
from flask import Blueprint, request
import aiohttp
from hypothesis.internal.reflection import proxies
import requests


from . import State, client_state


TIMEOUT: float = float(os.getenv("TIMEOUT", "2"))

SERVER_URL: str = os.getenv("SERVER_URL", "http://127.0.0.1:5000/")

REGISTRAR_URL: str = os.getenv("REGISTRAR_URL", "http://127.0.0.1:5001/")
LOGGER_URL: str = os.getenv("LOGGER_URL", "http://127.0.0.1:3000/")

CLIENT_URL: str = os.getenv("CLIENT_URL", "http://127.0.0.1:5004")

TOTAL_CLIENT: str = os.getenv("TOTAL_CLIENT", "3")

PROXY_URL: str = os.getenv("PROXY_URL", "http://127.0.0.1:5001")

bp = Blueprint("gossip", __name__)


@bp.route("/<string:resource_id>/request", methods=["POST"])
async def request_resource(resource_id: str) -> tuple[str, int]:
    if client_state.current_state[resource_id] == State.EXECUTING:
        return f"client is already executing resource {resource_id}", 200

    if client_state.current_state[resource_id] == State.DEFAULT:
        requests.put(
            f"{LOGGER_URL}{resource_id}/log",
            json={
                "type": "start",
                "client_url": request.host_url,
                "time": time(),
            },
        )

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

    return f"client REQUESTING {resource_id} to DEFAULT)", 202


@bp.route("/<string:resource_id>/token", methods=["PUT"])
async def receive_token(resource_id: str) -> tuple[str, int]:

    # if client_state.current_state[resource_id] == State.DEFAULT:

    #     pass_thread = threading.Thread(
    #         target=pass_token_wrapper,
    #         args=(resource_id),
    #     )

    #     pass_thread.start()
    #     return f"token {resource_id} passed", 200

    if client_state.current_state[resource_id] == State.REQUESTING:
        client_state.current_state[resource_id] = State.EXECUTING

        resp, code = await lock_resource(resource_id)
        print(f"client {request.host_url} has locked")
        client_state.current_state[resource_id] = State.DEFAULT
        # return resp, code

    pass_thread = threading.Thread(
        target=pass_token_wrapper,
        args=(resource_id),
    )

    pass_thread.start()

    # The only state remaining is EXECUTING but if the client is executing then
    # it is currently holding that token so it can't receive a token from somewhere else
    # return f"duplication of token for {resource_id}", 400
    return f"pass in  token for {resource_id}", 200


def pass_token_wrapper(resource_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(pass_token(resource_id))
    loop.close()


async def pass_token(resource_id: str) -> tuple[str, int]:
    next_url = client_state.get_next_client_url()
    async with aiohttp.ClientSession() as session:
        await session.put(
            f"{next_url}{resource_id}/token",
            proxy=PROXY_URL,
            json={},
        )

    return "passed", 200


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

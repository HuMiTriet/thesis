import asyncio
import os
import threading
from time import time


# from datetime import datetime
from flask import Blueprint, request
import aiohttp
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
        print(f"{request.host_url} is executing alr")
        return f"client is already executing resource {resource_id}", 200

    if client_state.current_state[resource_id] == State.DEFAULT:
        data = request.get_json()
        delay_time = data["delay_time"]
        client_no = data["client_no"]
        client_state.delay_time = delay_time

        # print(f"{request.host_url} default -> exe ")
        client_state.current_state[resource_id] = State.REQUESTING

        # print(f"{request.host_url} default -> exe (wait)")
    # await client_state.token_received_event.wait()
    # print(f"{request.host_url} default -> exe (DONE wait)")

    return f"client has requested {resource_id}", 200


@bp.route("/<string:resource_id>/lock", methods=["DELETE"])
async def delete_request(resource_id: str) -> tuple[str, int]:
    print(
        f"client {request.host_url} received DEL and current state {client_state.current_state[resource_id]}"
    )
    data = request.get_json()
    delay_time: str = data["delay_time"]
    client_no = data["client_no"]
    if client_state.current_state[resource_id] == State.REQUESTING:
        client_state.current_state[resource_id] = State.NOT_INTERESTED

        return (
            f"client cannot delete {resource_id} lock because has not yet hold it",
            401,
        )

    if client_state.current_state[resource_id] == State.EXECUTING:
        # client_state.token_received_event.clear()
        client_state.current_state[resource_id] = State.DEFAULT

        requests.put(
            f"{LOGGER_URL}{resource_id}/log",
            json={
                "type": "start",
                "client_url": request.host_url,
                "time": time(),
                "delay_time": delay_time,
                "client_no": client_no,
            },
        )
        await asyncio.gather(
            release_lock(resource_id, delay_time, client_no),
            pass_token(resource_id, delay_time, client_no),
        )

        return f"client release token {resource_id} and passed it along", 200

    # client_state.token_received_event.clear()
    return f"client REQUESTING {resource_id} to DEFAULT)", 202


@bp.route("/<string:resource_id>/token", methods=["PUT"])
async def receive_token(resource_id: str) -> tuple[str, int]:
    print(
        f"client {request.host_url} receive token and {client_state.current_state[resource_id]}"
    )
    delay_time = (
        "0.0" if client_state.delay_time is None else client_state.delay_time
    )

    data = request.get_json()
    client_no = data["client_no"]

    if client_state.current_state[resource_id] == State.NOT_INTERESTED:
        client_state.current_state[resource_id] = State.DEFAULT
        async with aiohttp.ClientSession() as session:
            await session.delete(
                f"{SERVER_URL}{resource_id}/lock",
                json={
                    "delay_time": delay_time,
                    "client_no": client_no,
                    "client_url": request.host_url,
                },
                proxy=PROXY_URL,
            )
        pass_thread = threading.Thread(
            target=pass_token_wrapper,
            args=(resource_id, delay_time, client_no),
        )

        pass_thread.start()
        return "async delete sucessful", 200

    if client_state.current_state[resource_id] == State.DEFAULT:
        print(
            f"{request.host_url} default (passing) to {client_state.get_next_client_url()} "
        )
        print("HERE")
        pass_thread = threading.Thread(
            target=pass_token_wrapper,
            args=(resource_id, delay_time, client_no),
        )

        pass_thread.start()
        return f"token {resource_id} passed", 200

    if client_state.current_state[resource_id] == State.REQUESTING:
        client_state.current_state[resource_id] = State.EXECUTING

        print(f"{request.host_url} exe -> lock")
        client_state.host_url = request.host_url
        resp, code = await lock_resource(resource_id, delay_time, client_no)
        print(f"lock done {resp} {code}")
        print(f"{request.host_url} lock -> default (done)")

        # print(f"client {request.host_url} has locked")
        client_state.current_state[resource_id] = State.DEFAULT

        # client_state.token_received_event.set()

        pass_thread = threading.Thread(
            target=pass_token_wrapper,
            args=(resource_id, delay_time, client_no),
        )

        pass_thread.start()
        return resp, code

    # The only state remaining is EXECUTING but if the client is executing then
    # it is currently holding that token so it can't receive a token from somewhere else
    return f"duplication of token for {resource_id}", 400
    # return f"pass in  token for {resource_id}", 200


def pass_token_wrapper(resource_id: str, delay_time: str, client_no: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(pass_token(resource_id, delay_time, client_no))
    loop.close()


async def pass_token(
    resource_id: str, delay_time: str, client_no: str
) -> tuple[str, int]:
    next_url = client_state.get_next_client_url()
    async with aiohttp.ClientSession() as session:
        await session.put(
            f"{next_url}{resource_id}/token",
            json={
                "delay_time": delay_time,
                "client_no": client_no,
            },
            proxy=PROXY_URL,
        )
    return "passed", 200


async def lock_resource(
    resource_id: str, delay_time: str, client_no: str
) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        print("client lockingg")
        # client_state.token_received_event.set()
        async with session.put(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "origin": request.host_url,
                "delay_time": delay_time,
                "client_no": client_no,
                "client_url": client_state.host_url,
            },
            proxy=PROXY_URL,
        ) as response:
            text, code = await response.text(), response.status

    return text, code


async def release_lock(
    resource_id: str, delay_time: str, client_no: str
) -> tuple[str, int]:
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{SERVER_URL}{resource_id}/lock",
            json={
                "delay_time": delay_time,
                "client_no": client_no,
                "client_url": request.host_url,
            },
            proxy=PROXY_URL,
        ) as response:
            return await response.text(), response.status

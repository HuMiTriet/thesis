import os
import json
from multiprocessing import Process
from signal import SIGTERM
from dotenv import load_dotenv  # or SIGKILL

from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
import pytest
import requests

from psutil import process_iter, AccessDenied

from server import create_app as create_server
from server_lamport import create_app as create_server_lamport
from registrar import create_app as create_registrar
from client import create_app as create_client
from client_lamport import create_app as create_client_lamport
from client_maekawa import create_app as create_client_maekawa
from proxy import create_app as create_proxy


SCOPE = "session"
load_dotenv()


@pytest.fixture(scope=SCOPE)
def server_app() -> Flask:
    return create_server()


@pytest.fixture(scope=SCOPE)
def server_lamport_app() -> Flask:
    return create_server_lamport()


@pytest.fixture(scope=SCOPE)
def registrar_app() -> Flask:
    return create_registrar()


@pytest.fixture(scope=SCOPE)
def client_app() -> Flask:
    return create_client()


@pytest.fixture(scope=SCOPE)
def client_lamport_app() -> Flask:
    return create_client_lamport()


@pytest.fixture(scope=SCOPE)
def client_maekawa_app() -> Flask:
    return create_client_maekawa()


@pytest.fixture(scope=SCOPE)
def proxy_app() -> Flask:
    return create_proxy()


@pytest.fixture
def server_client(
    server_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskClient:
    return server_app.test_client()


@pytest.fixture
def registrar_client(
    registrar_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskClient:
    return registrar_app.test_client()


@pytest.fixture
def client_client(
    client_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskClient:
    return client_app.test_client()


@pytest.fixture
def server_cli_runner(
    server_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskCliRunner:
    return server_app.test_cli_runner()


@pytest.fixture
def registrar_cli_runner(
    registrar_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskCliRunner:
    return registrar_app.test_cli_runner()


@pytest.fixture
def client_cli_runner(
    client_app: Flask,  # pylint: disable=redefined-outer-name
) -> FlaskCliRunner:
    return client_app.test_cli_runner()


def kill_process(ports: list[int]) -> None:

    for proc in process_iter():
        try:
            for conns in proc.connections(kind="inet"):
                if conns.laddr.port in ports:
                    proc.send_signal(SIGTERM)
        except AccessDenied:
            pass


def reset_dummy_data() -> None:
    with open(os.path.join("dummy_data.json"), "r", encoding="utf-8") as file:
        data = json.load(file)

    for item in data:
        if item["is_locked"]:
            item["is_locked"] = False

    with open(os.path.join("dummy_data.json"), "w", encoding="utf-8") as file:
        json.dump(data, file)


@pytest.fixture(scope=SCOPE)
def setup(
    server_app: Flask,  # pylint: disable=redefined-outer-name
    registrar_app: Flask,  # pylint: disable=redefined-outer-name
    client_app: Flask,  # pylint: disable=redefined-outer-name
    proxy_app: Flask,  # pylint: disable=redefined-outer-name
):

    kill_process([5000, 5001, 5002, 5003, 5004])
    # kill any process at port 5000 5001 5002 and 5003
    # print("STARTING SERVER...")

    proxy_process = Process(target=proxy_app.run, kwargs={"port": 5004})
    server_process = Process(target=server_app.run, kwargs={"port": 5000})
    registrar_process = Process(
        target=registrar_app.run, kwargs={"port": 5001}
    )
    client_1_process = Process(target=client_app.run, kwargs={"port": 5002})
    client_2_process = Process(target=client_app.run, kwargs={"port": 5003})

    proxy_process.start()
    server_process.start()
    registrar_process.start()
    client_1_process.start()
    client_2_process.start()

    yield

    #    print("KILLING SERVER")

    proxy_process.terminate()
    server_process.terminate()
    registrar_process.terminate()
    client_1_process.terminate()
    client_2_process.terminate()

    kill_process([5000, 5001, 5002, 5003, 5004])
    reset_dummy_data()


@pytest.fixture(scope=SCOPE)
def setup_no_registrar(
    server_app: Flask,  # pylint: disable=redefined-outer-name
    client_app: Flask,  # pylint: disable=redefined-outer-name
    proxy_app: Flask,  # pylint: disable=redefined-outer-name
):

    kill_process([5000, 5002, 5003, 5004])

    server_process = Process(target=server_app.run, kwargs={"port": 5000})
    client_1_process = Process(target=client_app.run, kwargs={"port": 5002})
    client_2_process = Process(target=client_app.run, kwargs={"port": 5003})
    proxy_process = Process(target=proxy_app.run, kwargs={"port": 5004})

    proxy_process.start()
    server_process.start()
    client_1_process.start()
    client_2_process.start()

    yield

    #    print("KILLING SERVER")

    proxy_process.terminate()
    server_process.terminate()
    client_1_process.terminate()
    client_2_process.terminate()

    kill_process([5000, 5002, 5003, 5004])
    reset_dummy_data()


@pytest.fixture(scope=SCOPE)
def setup_server_and_proxy(
    server_lamport_app: Flask,  # pylint: disable=redefined-outer-name
    proxy_app: Flask,  # pylint: disable=redefined-outer-name
):
    kill_process([5000, 5001])

    server_process = Process(
        target=server_lamport_app.run, kwargs={"port": 5000}
    )

    proxy_process = Process(target=proxy_app.run, kwargs={"port": 5001})

    server_process.start()
    proxy_process.start()

    yield

    server_process.terminate()
    proxy_process.terminate()

    kill_process([5000, 5001])


@pytest.fixture(scope=SCOPE)
def setup_ricart_agrawala_four_client(
    setup_server_and_proxy,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
    client_lamport_app: Flask,  # pylint: disable=redefined-outer-name
):
    kill_process([5002, 5003, 5004, 5005])

    client_1_process = Process(
        target=client_lamport_app.run, kwargs={"port": 5002}
    )

    client_2_process = Process(
        target=client_lamport_app.run, kwargs={"port": 5003}
    )

    client_3_process = Process(
        target=client_lamport_app.run, kwargs={"port": 5004}
    )

    client_4_process = Process(
        target=client_lamport_app.run, kwargs={"port": 5005}
    )

    client_1_process.start()
    client_2_process.start()
    client_3_process.start()
    client_4_process.start()

    yield

    #    print("KILLING SERVER")

    client_1_process.terminate()
    client_2_process.terminate()
    client_3_process.terminate()
    client_4_process.terminate()

    kill_process([5002, 5003, 5004, 5005])


@pytest.fixture(scope=SCOPE)
def setup_maekawa_four_client(
    setup_server_and_proxy,  # pyright: ignore  # pylint: disable=unused-argument,redefined-outer-name
    client_maekawa_app: Flask,  # pylint: disable=redefined-outer-name
):
    kill_process([5002, 5003, 5004, 5005])

    client_1_process = Process(
        target=client_maekawa_app.run, kwargs={"port": 5002}
    )

    client_2_process = Process(
        target=client_maekawa_app.run, kwargs={"port": 5003}
    )

    client_3_process = Process(
        target=client_maekawa_app.run, kwargs={"port": 5004}
    )

    client_4_process = Process(
        target=client_maekawa_app.run, kwargs={"port": 5005}
    )

    client_1_process.start()
    client_2_process.start()
    client_3_process.start()
    client_4_process.start()

    yield

    client_1_process.terminate()
    client_2_process.terminate()
    client_3_process.terminate()
    client_4_process.terminate()

    kill_process([5002, 5003, 5004, 5005])


@pytest.fixture(scope=SCOPE)
def register_client(
    setup,  # pyright: ignore # pylint: disable=unused-argument,redefined-outer-name
):
    response = requests.post(
        "http://127.0.0.1:5002/register",
        timeout=5,
    )
    assert response.status_code == 200

    response = requests.post(
        "http://127.0.0.1:5003/register",
        timeout=5,
    )
    assert response.status_code == 200


@pytest.fixture(autouse=False, scope="session")
def load_faults_into_proxy():
    with open(
        os.path.join("faults.json"),
        "r",
        encoding="utf-8",
    ) as file:

        all_faults = json.load(file)

        for fault in all_faults:
            requests.post(
                "http://127.0.0.1:5004/fault",
                json=fault,
                timeout=5,
            )

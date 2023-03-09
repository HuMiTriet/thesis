from flask.testing import FlaskCliRunner, FlaskClient
from multiprocessing import Process
import pytest

from flask import Flask
import requests
from server import create_app as create_server
from registrar import create_app as create_registrar
from client import create_app as create_client


@pytest.fixture
def server_app() -> Flask:
    return create_server()


@pytest.fixture
def registrar_app() -> Flask:
    return create_registrar()


@pytest.fixture
def client_app() -> Flask:
    return create_client()


@pytest.fixture
def server_client(server_app: Flask) -> FlaskClient:
    return server_app.test_client()


@pytest.fixture
def registrar_client(registrar_app: Flask) -> FlaskClient:
    return registrar_app.test_client()


@pytest.fixture
def client_client(client_app: Flask) -> FlaskClient:
    return client_app.test_client()


@pytest.fixture
def server_cli_runner(server_app: Flask) -> FlaskCliRunner:
    return server_app.test_cli_runner()


@pytest.fixture
def registrar_cli_runner(registrar_app: Flask) -> FlaskCliRunner:
    return registrar_app.test_cli_runner()


@pytest.fixture
def client_cli_runner(client_app: Flask) -> FlaskCliRunner:
    return client_app.test_cli_runner()


@pytest.fixture
def setup(server_app: Flask, registrar_app: Flask, client_app: Flask):

    server_process = Process(target=server_app.run, kwargs={"port": 5000})
    registrar_process = Process(
        target=registrar_app.run, kwargs={"port": 5001}
    )
    client_1_process = Process(target=client_app.run, kwargs={"port": 5002})
    client_2_process = Process(target=client_app.run, kwargs={"port": 5003})

    server_process.start()
    registrar_process.start()
    client_1_process.start()
    client_2_process.start()

    yield

    server_process.terminate()
    registrar_process.terminate()
    client_1_process.terminate()
    client_2_process.terminate()

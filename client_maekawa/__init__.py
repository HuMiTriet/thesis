import os

from asyncio import Queue
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from flask import Flask
import requests
from werkzeug.exceptions import InternalServerError


@dataclass
class ClientRequest:
    url: str = ""
    resource_id: str = ""


@dataclass
class ClientState:
    queued_request: Queue = field(default_factory=Queue)
    quorum_urls: list[str] = field(default_factory=list)
    currently_using_resource_id: set[str] = field(default_factory=set)

    def get_quorum_urls(self, url: str) -> list[str]:
        if len(self.quorum_urls) == 0:
            env_vars = os.environ

            # Filter out environment variables that start with 'QUORUM_'
            quorum_vars = {
                key: value
                for key, value in env_vars.items()
                if key.startswith("QUORUM_")
            }

            # Split the quorum values into lists of strings
            quorums = [value.split(" ") for value in quorum_vars.values()]

            # Initialize an empty list to accumulate URLs from all quorums
            all_quorum_urls = []

            # Check if the url is in each of the list[str]
            for quorum in quorums:
                if url in quorum:
                    # Extend the all_quorum_urls list with URLs from the quorum,
                    # excluding the provided URL
                    all_quorum_urls.extend(
                        [
                            quorum_url
                            for quorum_url in quorum
                            if quorum_url != url
                        ]
                    )

            self.quorum_urls = all_quorum_urls

        return self.quorum_urls


client_state = ClientState()


def create_app():
    """
    The factory function that returns an instance of the client.

    A client is an entity that interact with a resource in acquiring locks and
    or releasing it.
    """
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    # pylint: disable=import-outside-toplevel
    from . import gossip

    app.register_blueprint(gossip.bp)

    @app.errorhandler(InternalServerError)
    def custom_error_msg(error: InternalServerError):  # pyright: ignore
        return f"CLIENT Err {str(error.__repr__)}", 500

    return app

from collections import defaultdict
from enum import Enum
import os


from dataclasses import dataclass, field

# from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError


class State(Enum):
    DEFAULT = 0
    REQUESTING = 1
    EXECUTING = 2


@dataclass()
class ClientState:
    current_state: defaultdict[str, State] = field(
        default_factory=lambda: defaultdict(lambda: State.DEFAULT)
    )

    def get_next_client_url(self, host_url: str) -> str | None:
        all_urls = os.getenv(
            "TOKEN_RING",
            """http://127.0.0.1:5002/ http://127.0.0.1:5003/
                http://127.0.0.1:5004/ http://127.0.0.1:5005/""",
        ).split(" ")

        total_clients = len(all_urls)
        for url_index, url in enumerate(all_urls):
            if url == host_url:
                return all_urls[(url_index + 1) % total_clients]

        return None


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

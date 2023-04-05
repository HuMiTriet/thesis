from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError

from lamport_clock import LamportClock


class ClientState(Enum):
    DEFAULT = 0
    REQUESTING = 1
    EXECUTING = 2


@dataclass
class State:
    lamport_clock: LamportClock = LamportClock()
    current_state: ClientState = ClientState.DEFAULT
    requesting_resource: set[str] = field(default_factory=set[str])
    approvals: dict[str, int] = field(default_factory=dict[str, int])
    executing_resource: set[str] = field(default_factory=set[str])
    deffered_replies: list[dict[str, str]] = field(
        default_factory=list[dict[str, str]]
    )


state = State()


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

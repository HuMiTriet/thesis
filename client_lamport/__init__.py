from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError

from lamport_clock import LamportClock


class State(Enum):
    REQUESTING = 0
    EXECUTING = 1


@dataclass(slots=True, kw_only=True)
class ResourceState:
    current_state: State = field(default=State.REQUESTING)
    approvals: int = field(default=0)


@dataclass
class ClientState:
    lamport_clock: LamportClock = LamportClock()
    deffered_replies: list[dict[str, str]] = field(
        default_factory=list[dict[str, str]]
    )
    resource_states: dict[str, ResourceState] = field(
        default_factory=dict[str, ResourceState]
    )


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

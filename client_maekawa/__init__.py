import os


from dataclasses import dataclass, field
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError


@dataclass
class ClientRequest:
    url: str = ""
    approvals: int = 0
    already_given_approvals: set[str] = field(default_factory=set[str])
    timeout: int = 10
    expiration_time: datetime = field(init=False)

    def __post_init__(self):
        self.expiration_time = datetime.now() + timedelta(seconds=self.timeout)


@dataclass
class ClientState:
    # queued_request: Queue[ClientRequest] = field(default_factory=Queue)
    _queued_request: dict[str, list[ClientRequest]] = field(
        default_factory=dict[str, list[ClientRequest]]
    )
    _quorum_urls: list[str] = field(default_factory=list)

    def get_resource_queue(self, resource_id: str) -> list[ClientRequest]:
        if self._queued_request.get(resource_id) is None:
            self._queued_request[resource_id] = []

        return self._queued_request[resource_id]

    def get_broadcast_urls(self, url: str) -> list[str]:
        if len(self._quorum_urls) == 0:
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

            self._quorum_urls = all_quorum_urls

        return self._quorum_urls


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

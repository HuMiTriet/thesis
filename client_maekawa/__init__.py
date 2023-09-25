from collections import defaultdict
import os
from math import sqrt, ceil


from dataclasses import dataclass, field

# from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError


@dataclass
class ClientRequest:
    url: str = ""
    approvals: int = 0
    already_given_approvals: set[str] = field(default_factory=set[str])
    # timeout: int = 10
    # expiration_time: datetime = field(init=False)

    # def __post_init__(self):
    #     self.expiration_time = datetime.now() + timedelta(seconds=self.timeout)


@dataclass
class ClientState:
    # queued_request: Queue[ClientRequest] = field(default_factory=Queue)
    _queued_request: defaultdict[str, list[ClientRequest]] = field(
        default_factory=lambda: defaultdict(list)
    )

    _quorum_urls: list[str] = field(default_factory=list)

    def get_request_queue(self, resource_id: str) -> list[ClientRequest]:
        return self._queued_request[resource_id]

    def _get_url_matrix(self) -> list[list[None]]:
        all_urls_str: str
        with open("client_urls.txt", "r") as file:
            all_urls_str = file.read()

        if all_urls_str is None:
            raise RuntimeError("Client url env var is not set")

        all_urls = all_urls_str.split()

        # Calculate k and create a 2D list of size k x k
        k = ceil(sqrt(len(all_urls)))
        url_matrix = [[None] * k for _ in range(k)]

        # Fill the 2D list with URLs
        for idx, url_item in enumerate(all_urls):
            row_idx = idx // k
            col_idx = idx % k
            url_matrix[row_idx][col_idx] = url_item  # pyright: ignore

        return url_matrix

    def get_broadcast_urls(self, target_url: str) -> list[str]:
        if len(self._quorum_urls) == 0:
            matrix = self._get_url_matrix()

            # Find the row and column indices of the target element
            row_idx, col_idx = None, None
            for i, row in enumerate(matrix):
                if target_url in row:
                    row_idx = i
                    col_idx = row.index(target_url)
                    break

            if row_idx is not None and col_idx is not None:
                # Get all the elements in the same row, excluding the target element and None values
                row_elements: list[str] = [
                    element
                    for i, element in enumerate(matrix[row_idx])
                    if i != col_idx and element is not None
                ]

                # Get all the elements in the same column, excluding the target
                # element and None values
                col_elements: list[str] = [  # pyright: ignore
                    row[col_idx]
                    for i, row in enumerate(matrix)
                    if i != row_idx and row[col_idx] is not None
                ]

                self._quorum_urls = row_elements + col_elements

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

from math import sqrt, ceil


from dataclasses import dataclass, field

# from datetime import datetime, timedelta


@dataclass
class ClientRequest:
    url: str = ""
    approvals: int = 0
    already_given_approvals: set[str] = field(default_factory=set[str])


@dataclass
class ClientState:
    # queued_request: Queue[ClientRequest] = field(default_factory=Queue)
    _queued_request: dict[str, list[ClientRequest]] = field(
        default_factory=dict[str, list[ClientRequest]]
    )

    _quorum_urls: list[str] = field(default_factory=list)

    def get_request_queue(self, resource_id: str) -> list[ClientRequest]:
        if self._queued_request.get(resource_id) is None:
            self._queued_request[resource_id] = []

        return self._queued_request[resource_id]

    def _get_url_matrix(self, all_urls_str: str) -> list[list[None]]:

        # all_urls_str = os.getenv(
        #     "CLIENT_URL",
        #     """http://127.0.0.1:5002/ http://127.0.0.1:5003/
        #            http://127.0.0.1:5004/ http://127.0.0.1:5005/
        #            """,
        # )

        # Split the string into a list of URLs
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

    def get_broadcast_urls(self, target_url: str, all_urls: str) -> list[str]:
        matrix = self._get_url_matrix(all_urls)
        result: list[str] = []

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

            result = row_elements + col_elements

        return result


client_state = ClientState()

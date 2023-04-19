from math import ceil, sqrt
import re

from hypothesis import given
from hypothesis.strategies import from_regex, sets

from client_maekawa.client_state import ClientState


@given(
    sets(
        from_regex(re.compile(r"^http://127\.0\.0\.1:[0-9]{4}/$")),
        min_size=1,
    )
)
def test_get_broadcast_url(all_urls: set[str]):
    # print(all_urls)
    delimiter = " "
    all_urls = {s.strip() for s in all_urls}
    K = ceil(sqrt(len(all_urls)))
    joined_string = delimiter.join(all_urls)

    client_state = ClientState()

    broadcast_urls_results = {}

    for client_url in all_urls:
        result = client_state.get_broadcast_urls(client_url, joined_string)

        # Test property 0: the result set should have K -1 element
        # (because the broadcast urls does not include the calling client itself)
        assert len(result) == K - 1 or len(result) == K

        # Test property 1: The set[str] Result does not include client_url itself
        assert client_url not in result

        # Need to do this append because the method get_broadcast_urls return a
        # list of url that exclude the original client_url
        result.append(client_url)

        broadcast_urls_results[client_url] = set(result)

    # Test property 2: Each result set from each client url has at least 1 common element
    for client_url, broadcast_urls in broadcast_urls_results.items():
        for (
            other_client_url,
            other_broadcast_urls,
        ) in broadcast_urls_results.items():
            if client_url != other_client_url:
                common_elements = broadcast_urls.intersection(
                    other_broadcast_urls
                )
                assert len(common_elements) >= 1

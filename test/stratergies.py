import os
import json

from hypothesis.strategies import SearchStrategy, lists, composite
from hypothesis import strategies as st


@composite
def resource(draw, size: int, min_codepoint: int = 65) -> SearchStrategy[str]:
    custom_character_strat = st.characters(
        min_codepoint=min_codepoint,
        max_codepoint=min_codepoint + 3,
    )
    keys = draw(
        lists(
            custom_character_strat, min_size=size, max_size=size, unique=True
        )
    )

    with open(os.path.join("dummy_data.json"), "w") as f:
        # format [{"id": key, "is_locked": false},]
        print("WRITING JSON")
        json.dump(
            [{"id": key, "is_locked": False} for key in keys], f, indent=4
        )

    return keys

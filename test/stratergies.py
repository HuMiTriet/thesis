from typing import Callable
from hypothesis.strategies import SearchStrategy, composite


# @composite
# def resource_id(
#     draw: Callable[[SearchStrategy], str], only_free_resources: bool = False
# ):
#     with open(os.path.join("dummy_data.json"), "r") as f:
#         import json

#         data = json.load(f)

# from typing import Callable
# from hypothesis.strategies import SearchStrategy, composite
# import os


# @composite
# def resource_id(draw: Callable[[SearchStrategy[str]], str]) -> list[str]:
#     result: list[str] = []

#     with open(os.path.join("../dummy_data.json"), "r") as f:
#         import json

#         data: list[dict] = json.load(f)

#         for json_object in data:
#             result.append(json_object["id"])

#     return hypothesis.strategies.sample_from(result)

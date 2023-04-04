import os
import json

from dataclasses import dataclass, field

from hypothesis.strategies import SearchStrategy, lists, composite
from hypothesis import strategies as st

from proxy.injectable_fault import InjectibleFault


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

    with open(os.path.join("dummy_data.json"), "w", encoding="utf-8") as file:
        # format [{"id": key, "is_locked": false},]
        json.dump(
            [{"id": key, "is_locked": False} for key in keys], file, indent=4
        )

    return keys


@composite
def fault_strategy(draw) -> InjectibleFault:
    choosen: list[str] = []

    fault_key_singleton = FaultKeySingleton()

    choosen = draw(
        st.lists(
            st.sampled_from(
                fault_key_singleton.get_fault_keys(),
            ),
            min_size=1,
        )
    )

    print(f"fault choosen {choosen}")

    return InjectibleFault(fault_names=choosen)


@dataclass(slots=True)
class FaultKeySingleton:

    _fault_keys: list[str] = field(default_factory=list[str], init=False)

    def get_fault_keys(self) -> list[str]:
        if len(self._fault_keys) == 0:
            with open(
                os.path.join("faults.json"),
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)
                for i in data:
                    self._fault_keys.append(i["name"])

        return self._fault_keys

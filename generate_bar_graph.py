import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

import pytest
import requests

result: dict[str, list[float]] = {}


def set_delay_injection_and_run(fault: str, test_path: str) -> list[float]:
    os.environ["FAULT_KEY"] = fault

    # Take the cli argument and replace it into the string below
    pytest.main([test_path])

    resp = requests.get("http://127.0.0.1:3000/stat", timeout=10)

    return resp.json()


parser = argparse.ArgumentParser(
    description="please specify the path to the test file"
)

parser.add_argument("test_path", help="path to the stateful test file")

args = parser.parse_args()

test_path = args.test_path


# no_delay = np.array(set_delay_injection_and_run("NULL", test_path))
# delay_small = np.array(
#     set_delay_injection_and_run("delay_all_small", test_path)
# )
# delay_medium = np.array(
#     set_delay_injection_and_run("delay_all_medium", test_path)
# )
# delay_large = np.array(
#     set_delay_injection_and_run("delay_all_large", test_path)
# )


# no_delay_mean = np.mean(no_delay)
# delay_small_mean = np.mean(delay_small)
# delay_medium_mean = np.mean(delay_medium)
# delay_large_mean = np.mean(delay_large)

# no_delay_std = np.std(no_delay)
# delay_small_std = np.std(delay_small)
# delay_medium_std = np.std(delay_medium)
# delay_large_std = np.std(delay_large)

# titles = ["no_delay", "delay_0.02", "delay_0.2", "delay_0.5"]
# x_pos = np.arange(len(titles))
# CTEs = [no_delay_mean, delay_small_mean, delay_medium_mean, delay_large_mean]
# error = [no_delay_std, delay_small_std, delay_medium_std, delay_large_std]

# # Build the plot
# fig, ax = plt.subplots()
# ax.bar(  # pyright: ignore
#     x_pos,
#     CTEs,
#     yerr=error,
#     align="center",
#     alpha=0.5,
#     ecolor="black",
#     capsize=10,
# )
# ax.set_ylabel("Time (in seconds)")  # pyright: ignore
# ax.set_xticks(x_pos)  # pyright: ignore
# ax.set_xticklabels(titles)  # pyright: ignore
# ax.set_title("algorithm with delay injections")  # pyright: ignore
# ax.yaxis.grid(True)  # pyright: ignore

# # Save the figure and show
# plt.tight_layout()
# # plt.savefig("maekawa_delay.png")
# plt.show()

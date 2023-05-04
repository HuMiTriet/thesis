import os
import numpy as np
import matplotlib.pyplot as plt

import pytest
import requests

result: dict[str, list[float]] = {}


def set_delay_injection_and_run(fault: str) -> list[float]:
    os.environ["FAULT_KEY"] = fault

    pytest.main(["./test/test_token_ring.py"])
    # http://127.0.0.1:3000/stat
    resp = requests.get("http://127.0.0.1:3000/stat", timeout=10)

    return resp.json()


# result["no_delay"] = set_delay_injection_and_run("NULL")
# result["delay_0.02"] = set_delay_injection_and_run("delay_all_small")
# result["delay_0.2"] = set_delay_injection_and_run("delay_all_medium")
# result["delay_0.5"] = set_delay_injection_and_run("delay_all_large")

no_delay = np.array(set_delay_injection_and_run("NULL"))
delay_small = np.array(set_delay_injection_and_run("delay_all_small"))
delay_medium = np.array(set_delay_injection_and_run("delay_all_medium"))
delay_large = np.array(set_delay_injection_and_run("delay_all_large"))

no_delay_mean = np.mean(no_delay)
delay_small_mean = np.mean(delay_small)
delay_medium_mean = np.mean(delay_medium)
delay_large_mean = np.mean(delay_large)

no_delay_std = np.std(no_delay)
delay_small_std = np.std(delay_small)
delay_medium_std = np.std(delay_medium)
delay_large_std = np.std(delay_large)

titles = ["no_delay", "delay_0.02", "delay_0.2", "delay_0.5"]
x_pos = np.arange(len(titles))
CTEs = [no_delay_mean, delay_small_mean, delay_medium_mean, delay_large_mean]
error = [no_delay_std, delay_small_std, delay_medium_std, delay_large_std]

# Build the plot
fig, ax = plt.subplots()
ax.bar(
    x_pos,
    CTEs,
    yerr=error,
    align="center",
    alpha=0.5,
    ecolor="black",
    capsize=10,
)
ax.set_ylabel("Time")
ax.set_xticks(x_pos)
ax.set_xticklabels(titles)
ax.set_title("fault injections")
ax.yaxis.grid(True)

# Save the figure and show
plt.tight_layout()
plt.savefig("bar_plot_with_error_bars.png")
plt.show()

import argparse
import json
import os
from collections import defaultdict
import typing
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from typing import Tuple
from matplotlib.axes import Axes


def read_json_data(filepath):
    with open(filepath, "r", encoding="UTF-8") as file:
        return json.load(file)


def group_by_delay_time(data):
    grouped_data = defaultdict(list)
    for entry in data:
        delay_time = float(entry["delay_time"])
        latency = entry["latency"]
        grouped_data[delay_time].append(latency)
    return grouped_data


def plot_scatter_and_slope(ax, x, y, label, color):
    ax.scatter(x, y, label=f"{label} (Points)", color=color, alpha=0.5)
    slope, intercept = np.polyfit(x, y, 1)
    ax.plot(
        x,
        slope * np.array(x) + intercept,
        label=f"{label} (Slope): {slope:.2f}",
        color=color,
        linestyle="--",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate scatter plot from multiple JSON data files."
    )
    parser.add_argument(
        "json_files", nargs="+", help="Paths to the JSON result files"
    )

    args = parser.parse_args()

    _, t = plt.subplots(figsize=(14, 10))
    ax = typing.cast(Axes, t)
    all_delay_times = set()

    for json_file in args.json_files:
        data = read_json_data(json_file)
        algorithm_name = os.path.splitext(os.path.basename(json_file))[0]
        formatted_algorithm_name = " ".join(
            word.capitalize() for word in algorithm_name.split("_")
        )

        grouped_data = group_by_delay_time(data)

        delay_times = []
        latencies = []

        for dt, lat in grouped_data.items():
            delay_times.extend([dt] * len(lat))
            latencies.extend(lat)

        plot_scatter_and_slope(
            ax, delay_times, latencies, formatted_algorithm_name, color=None
        )  # color=None will auto-assign colors

        all_delay_times.update(
            set(delay_times)
        )  # accumulate all delay_time values

    ax.set_xticks(sorted(list(all_delay_times)))  # set xticks explicitly
    ax.set_xticklabels(
        sorted(list(all_delay_times)), rotation=45
    )  # set xtick labels explicitly and rotate for better visibility

    ax.set_xlabel("Delay Time")
    ax.set_ylabel("Latency")
    ax.set_title("Latency by Algorithm with Slope Lines")
    ax.legend()

    FONTSIZE = 12
    plt.tick_params(axis="both", which="major", labelsize=FONTSIZE)

    plt.savefig("all_scater.svg", format="svg")
    plt.show()


if __name__ == "__main__":
    main()

import os
import argparse
from collections import defaultdict
import json
import statistics
import matplotlib.pyplot as plt
import numpy as np


parser = argparse.ArgumentParser(
    prog="generate bar graph from json data",
    description="please specify the path to the json file",
)

parser.add_argument("test_path", help="path to the json result file")

args = parser.parse_args()

test_path = args.test_path

print(test_path)

PARSED_DATA = None
algorithm_name = os.path.splitext(os.path.basename(test_path))[0]

with open(test_path, "r", encoding="UTF-8") as file:
    PARSED_DATA = json.load(file)

if PARSED_DATA is not None:
    # unserialize the json object
    grouped_data = defaultdict(list)

    for entry in PARSED_DATA:
        delay_time = entry["delay_time"]
        latency = float(entry["latency"])
        grouped_data[delay_time].append(latency)

    average_latency_per_group = {}
    std_dev_latency_per_group = {}

    for key, values in grouped_data.items():
        average_latency_per_group[key] = sum(values) / len(values)
        std_dev_latency_per_group[key] = (
            statistics.stdev(values) if len(values) > 1 else 0
        )

    labels = list(average_latency_per_group.keys())
    values = list(average_latency_per_group.values())
    std_devs = list(std_dev_latency_per_group.values())
    np_labels = np.array(list(map(float, labels)))
    np_values = np.array(values)

    # Calculate the correlation coefficient
    corr_coefficient = np.corrcoef(np_labels, np_values)[0, 1]
    coeff_determination = corr_coefficient**2

    plt.figure(figsize=(14, 9))
    plt.bar(
        labels,
        values,
        yerr=std_devs,
        capsize=10,
        alpha=0.7,
        color="blue",
        ecolor="black",
    )
    plt.xlabel("Delay Time")
    plt.ylabel("Average Latency")
    plt.title("Average Latency per Delay Time Group with Standard Deviation")
    FORMATTED_ALGORITHM_NAME = " ".join(
        word.capitalize() for word in algorithm_name.split("_")
    )
    plt.suptitle(f"{FORMATTED_ALGORITHM_NAME} algorithm")
    # plt.suptitle("Token ring algorithm")
    FONTSIZE = 12
    plt.tick_params(axis="both", which="major", labelsize=FONTSIZE)
    plt.xticks(rotation=45)
    plt.text(
        0.05,
        0.95,
        f"Coefficient of Correlation: {corr_coefficient:.2f}\nCoefficient of Determination: {coeff_determination:.2f}",
        horizontalalignment="left",
        verticalalignment="center",
        transform=plt.gca().transAxes,
        fontsize=12,
    )
    # plt.show()
    plt.savefig(f"{algorithm_name}.svg", format="svg")
    # plt.savefig("token_ring.svg", format="svg")

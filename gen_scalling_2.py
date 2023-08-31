import os
import json
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    prog="generate bar graph from json data",
    description="please specify the path to the json file",
)

parser.add_argument("test_path", help="path to the json result file")

args = parser.parse_args()

test_path = args.test_path

PARSED_DATA = None
algorithm_name = os.path.splitext(os.path.basename(test_path))[0]

with open(test_path, "r", encoding="UTF-8") as file:
    PARSED_DATA = json.load(file)

if PARSED_DATA is not None:
    # unserialize the json object
    grouped_data = defaultdict(list)

    for entry in PARSED_DATA:
        client_no = float(entry["client_no"])
        latency = float(entry["latency"])
        grouped_data[client_no].append(latency)

    # Now let's generate the scatter plot
    plt.figure(figsize=(14, 10))
    for client_no, latencies in grouped_data.items():
        # assert client_no == len(latencies)
        plt.scatter(
            [client_no] * len(latencies),
            latencies,
            color="blue",
        )

    # Aesthetic and informative elements
    plt.xlabel("Number of Client", fontsize=12)
    plt.ylabel("Latency (ms)", fontsize=12)
    plt.title(
        "Latency Variability Across Different number of Clients", fontsize=12
    )

    plt.show()
    plt.savefig(f"scalling_ricart.svg", format="svg")

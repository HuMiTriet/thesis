from collections import defaultdict
from dataclasses import dataclass
import logging
from flask import Flask, request
import statistics


app = Flask(__name__)


@dataclass
class Tally:
    total_time: float = 0.0
    number_of_reqeuest: int = 0

    def add_time_and_increment(self, time):
        self.total_time += time
        self.number_of_reqeuest += 1

    def get_avg_time(self) -> float:
        return self.total_time / self.number_of_reqeuest


existing_requests: dict[str, float] = {}
client_and_time: defaultdict[str, Tally] = defaultdict(Tally)


# split this into two different endpoints
@app.route("/<string:resource_id>/log", methods=["PUT"])
def index(resource_id: str):
    data = request.get_json()
    client_url: str = data["client_url"]
    log_type: str = data["type"]
    key = f"{client_url}-{resource_id}"
    logging.info("using key %s", key)
    time: float = data["time"]

    if log_type == "start":
        print(
            f"START: client {client_url} on {resource_id} with existing keys are {existing_requests.keys()}"
        )
        # if existing_requests.get(key) is None:
        existing_requests[key] = time

    elif log_type == "end":
        print(
            f"END: client {client_url} on {resource_id} with existing keys are {existing_requests.keys()}"
        )

        latency = time - existing_requests[key]

        client_and_time[client_url].add_time_and_increment(latency)

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    result: list[float] = []
    for tally in client_and_time.values():
        # getting individual time -> table (scatterplot) color by nodes
        result.append(tally.get_avg_time())

    real_result: list[float] = []
    real_result.append(statistics.fmean(result))

    existing_requests.clear()
    client_and_time.clear()

    return real_result, 200


# request
# check when it is lock


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

from collections import defaultdict
from dataclasses import dataclass
import json
import logging
from flask import Flask, jsonify, request


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


@app.route("/<string:resource_id>/log", methods=["POST", "PUT"])
def index(resource_id: str):
    data = request.get_json()
    client_url: str = data["client_url"]
    key = f"{client_url}-{resource_id}"
    logging.info("using key %s", key)
    time: float = data["time"]
    if request.method == "POST":
        if existing_requests.get(key) is None:
            existing_requests[key] = time

    elif request.method == "PUT":
        latency = time - existing_requests[key]
        logging.debug("it took %s : %s ", key, latency)
        client_and_time[client_url].add_time_and_increment(latency)

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    result: list[float] = []
    for tally in client_and_time.values():
        # result += f"client {client} delay stat: {tally.get_avg_time()} \n"
        result.append(tally.get_avg_time())

    existing_requests.clear()
    client_and_time.clear()

    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

from collections import defaultdict
from dataclasses import dataclass
import json
from flask import Flask, request


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


existing_request: dict[str, float] = {}
client_and_time: defaultdict[str, Tally] = defaultdict(Tally)


@app.route("/log", methods=["POST"])
def index():
    data = request.form
    if data["name"] == "root":
        msg = json.dumps(data["msg"])
        print(msg)
        if existing_request.get(msg) is None:
            existing_request[msg] = float(data["created"])
        else:
            delay = float(data["created"]) - existing_request[msg]
            print(f"it took {msg} {delay}")
            url = msg.split()[0].replace('"', "")
            client_and_time[url].add_time_and_increment(delay)

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    result: str = ""
    for client, tally in client_and_time.items():
        result += f"client {client} delay stat: {tally.get_avg_time()} \n"

    existing_request.clear()
    client_and_time.clear()

    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

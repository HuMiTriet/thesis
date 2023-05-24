import json
from dataclasses import dataclass, asdict
import statistics
from flask import Flask, request
import redis

app = Flask(__name__)
redis_connection = redis.Redis()


@app.route("/<string:resource_id>/log", methods=["PUT"])
def index(resource_id: str):
    data = request.get_json()
    client_url: str = data["client_url"]
    log_type: str = data["type"]
    key = f"{client_url}-{resource_id}"
    time: float = data["time"]

    if log_type == "start":
        redis_connection.set(key, time)

    elif log_type == "end":
        latency = time - float(redis_connection.get(key) or 0)

        # print(f"latency for {client_url} is {latency}")

        redis_connection.rpush("latencies", latency)

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    latencies = [float(x) for x in redis_connection.lrange("latencies", 0, -1)]

    redis_connection.flushall()
    return latencies, 200


@app.route("/stat_median", methods=["GET"])
def median():
    latencies = [float(x) for x in redis_connection.lrange("latencies", 0, -1)]
    median_latency = statistics.median(latencies) if latencies else 0

    result: list[float] = []
    result.append(median_latency)
    redis_connection.flushall()
    return result, 200


@app.route("/stat_mean", methods=["GET"])
def mean():
    latencies = [float(x) for x in redis_connection.lrange("latencies", 0, -1)]

    median_latency = statistics.fmean(latencies) if latencies else 0

    result: list[float] = []
    result.append(median_latency)
    redis_connection.flushall()
    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

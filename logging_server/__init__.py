import json
from dataclasses import dataclass
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
    delay_time: str = data["delay_time"]
    key = f"{client_url}-{resource_id}-{delay_time}"
    time: float = data["time"]

    if log_type == "start":
        # print(f"START: {key}")
        redis_connection.set(key, time)

    elif log_type == "end":
        # print(f"END: {key}")
        start_time = redis_connection.get(key)
        if start_time is None:
            print(f"Warning: No start time for key: {key}")
            # Optionally handle this case further, e.g., return an error status
        else:
            latency = time - float(start_time)
            latency_data = json.dumps(
                {"latency": latency, "delay_time": delay_time}
            )
            redis_connection.rpush("latencies", latency_data)

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    latencies_data = [
        json.loads(x) for x in redis_connection.lrange("latencies", 0, -1)
    ]

    redis_connection.flushall()
    return latencies_data, 200


@app.route("/stat_median", methods=["GET"])
def median():
    latencies_data = [
        json.loads(x) for x in redis_connection.lrange("latencies", 0, -1)
    ]
    latencies = [x["latency"] for x in latencies_data]
    delay_time = latencies_data[0]["delay_time"] if latencies_data else None

    median_latency = statistics.median(latencies) if latencies else 0

    result = {
        "median_latency": median_latency,
        "delay_time": delay_time,
    }
    # print(f"result from stat_median {result}")
    redis_connection.flushall()
    return result, 200


@app.route("/stat_mean", methods=["GET"])
def mean():
    latencies_data = [
        json.loads(x) for x in redis_connection.lrange("latencies", 0, -1)
    ]
    latencies = [x["latency"] for x in latencies_data]
    delay_times = [x["delay_time"] for x in latencies_data]

    mean_latency = statistics.fmean(latencies) if latencies else 0

    result = {
        "mean_latency": mean_latency,
        "delay_times": delay_times,
    }
    redis_connection.flushall()
    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

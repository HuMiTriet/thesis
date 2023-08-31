import statistics
from flask import Flask, request

app = Flask(__name__)
# redis_connection = redis.Redis()

latency_dict: dict[str, float] = {}
latency_tally: list[dict[str, float | str]] = []


@app.route("/<string:resource_id>/log", methods=["PUT"])
def log(resource_id: str):
    data = request.get_json()
    client_url: str = data["client_url"]
    log_type: str = data["type"]
    delay_time: str = data["delay_time"]
    client_no: str = data["client_no"]
    key = f"{client_url}-{client_no}-{delay_time}"
    time: float = data["time"]
    # print(f"request from {client_url} with type {log_type}")

    if log_type == "start":
        # redis_connection.set(key, time)
        print(f"start {key}")
        latency_dict[key] = time

    elif log_type == "end":
        # start_time = redis_connection.get(key)
        start_time = latency_dict.get(key)
        print(f"end {key}")
        if start_time is None:
            print(f"Warning: No start time for key: {key}")
            # Optionally handle this case further, e.g., return an error status
        else:
            latency = time - float(start_time)
            # latency_data = json.dumps(
            #     {"latency": latency, "delay_time": delay_time}
            # )
            # redis_connection.rpush("latencies", latency_data)

            latency_tally.append(
                {
                    "latency": latency,
                    "delay_time": delay_time,
                    "client_no": client_no,
                }
            )

    return ""


@app.route("/stat", methods=["GET"])
def stat():
    result = latency_tally.copy()
    latency_tally.clear()
    latency_dict.clear()

    return result, 200


@app.route("/stat_median", methods=["GET"])
def median():
    # result = result_container
    # latencies_data = [
    #     json.loads(x) for x in redis_connection.lrange("latencies", 0, -1)
    # ]
    latencies = [float(x["latency"]) for x in latency_tally]

    delay_time = latency_tally[0]["delay_time"] if latency_tally else None

    median_latency = statistics.median(latencies) if latencies else 0

    result = {
        "median_latency": median_latency,
        "delay_time": delay_time,
    }
    # print(f"result from stat_median {result}")
    # redis_connection.flushall()
    latency_tally.clear()
    latency_dict.clear()
    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

import redis

r = redis.Redis(host="localhost", port=6379, db=0)

r.set("existing_requests", "foo")
print(r.get("existing_requests"))

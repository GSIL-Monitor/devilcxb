import redis

redis_client = redis.Redis(password="test")
# redis_client.set("name", 1)
print redis_client.get("name")
print redis_client.dbsize()
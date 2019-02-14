import redis
import logging
from rediscluster import StrictRedisCluster

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class RedisHandle(object):
    def __init__(self, host, port, db=0):
        nodes = [{"host": host, "port": port}]
        self.redis_client = StrictRedisCluster(startup_nodes=nodes, decode_responses=True)
        # self.redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def get(self, redis_key):
        logging.info("start to get value of redis_key: %s" % (redis_key))
        return self.redis_client.get(redis_key)

    def delete(self, redis_key):
        logging.info("start to match redis_key: %s" % (redis_key))
        keys = self.redis_client.keys(redis_key + "*")
        for key in keys:
            logging.info("start to delete redis_key: %s" % (key))
            self.redis_client.delete(key)


if __name__ == '__main__':
    r = RedisHandle(host='10.40.10.82', port=7001, db=0)
    print r.get("{zhenliang}:doingcallback:{list}")
    # print r.delete("phone")

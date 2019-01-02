# -*- coding:utf-8 -*-

from rediscluster import StrictRedisCluster

redis_nodes = [
    {'host': '192.168.2.101', 'port': 7000},
    {'host': '192.168.2.101', 'port': 7001},
    {'host': '192.168.2.101', 'port': 7002},
    {'host': '192.168.2.101', 'port': 7003},
    {'host': '192.168.2.101', 'port': 7004},
    {'host': '192.168.2.101', 'port': 7005},
]


class RedisCluster(object):
    def __init__(self, redis_nodes):
        self.cluster = StrictRedisCluster(startup_nodes=redis_nodes)

    # 无差别的方法
    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.cluster.set(name, value, ex, px, nx, xx)

    # 无差别的方法
    def get(self, name):
        return self.cluster.get(name)

    # 扇形发送的命令
    def cluster_info(self):
        return self.cluster.cluster_info()

    # 重写StrictRedis的方法
    def mset(self, *args, **kwargs):
        return self.cluster.mset(args, kwargs)

    # 重写StrictRedis的方法
    def mget(self, keys, *args):
        return self.cluster.mget(keys, args)

if __name__ == '__main__':
    cluster = RedisCluster(redis_nodes)
    cluster.cluster_info()
    cluster.set("name", "mike")
    print cluster.get("name")

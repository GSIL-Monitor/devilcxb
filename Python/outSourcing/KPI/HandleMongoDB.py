# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import *


class HandleMongoDB(object):
    def __init__(self, host, port):
        """
        初始化Mongodb的客户端连接
        :param host: 数据库的地址
        :param port: 开启的Mongodb的端口
        :return:
        """
        self.client = MongoClient(host, port)

    def get_db(self, db_name):
        """
        通过传入的数据库名称获取数据库的对象
        :param db_name: 数据库名称
        :return: 数据库对象
        """
        return self.client[db_name]

    def get_table(self, db_obj, table_name):
        """
        通过传入的数据库的对象获取table的对象
        :param db_obj: 数据库的对象，可通过get_db获取
        :param table_name:表名称，在mongodb里面为collection
        :return: 返回数据表的可操作对象
        """
        return db_obj[table_name]

    def query_table(self, table_obj, conditions, fileds=None):
        """
        返回通过通过条件查询出来的结果
        :param table_obj: 数据表的对象
        :param conditions: 查询条件，如{"deviceID": "aaabbtest"}
        :param fileds: 查询的字段，如{"deviceID": 1}
        :return: 返回查询的结果
        """
        return map(lambda x: x, table_obj.find(conditions, fileds))

    def insert_item(self, table_obj, data):
        """
        插入新数据
        :param table_obj: 数据表的对象
        :param data: 需要插入的数据
        :return: None
        """
        table_obj.insert(data)

    def update_item(self, table_obj, condition, data):
        """
        更新数据
        :param table_obj: 数据表的对象
        :param condition: 查询的条件
        :param data: 更新的数据
        :return: None
        """
        table_obj.update(condition, data)

    def delete_items(self, table_obj, condition):
        """
        删除数据
        :param condition:
        :return: None
        """
        table_obj.delete_many(condition)

    def close_mongodb(self):
        """
        关闭mongoDB的链接
        :return: None
        """
        self.client.close()


if __name__ == "__main__":
    HandleMongoDB = HandleMongoDB("10.115.101.231", 27017)
    db_obj = HandleMongoDB.get_db("Device")
    table_obj = HandleMongoDB.get_table(db_obj, "projectMapping")
    data = map(lambda x: x["deviceID"], HandleMongoDB.query_table(table_obj, {"project": "monkey"}, {"deviceID": 1}))
    from Tools.HandleJenkins.HandleJenkins import HandleJenkins
    HandleJenkins = HandleJenkins("http://10.115.101.230:8080/jenkins/", "jenkins.cdval", "I8IBz0U2TC")
    print data
    allNodes = HandleJenkins.get_all_nodes()
    matchedNodes = filter(lambda x: x.split("_")[-1] in data, allNodes)
    matchedNodes = filter(lambda x: HandleJenkins.is_node_online(x), matchedNodes)
    nodes_runingPending_items = {}
    for matchedNode in matchedNodes:
        if HandleJenkins.is_node_idle(matchedNode):
            nodes_runingPending_items[matchedNode] = len(HandleJenkins.query_items(matchedNode))
        else:
            nodes_runingPending_items[matchedNode] = len(HandleJenkins.query_items(matchedNode)) + 1
    min_nodes_runingPending_items = min(nodes_runingPending_items.values())
    availableNodes = filter(lambda x: nodes_runingPending_items[x] == min_nodes_runingPending_items, nodes_runingPending_items)
    print availableNodes
    import random
    print random.choice(availableNodes)

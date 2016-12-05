# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import *
from math import *


class HandleDatabase(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client['jingqu_db_test']
        self.jingqu_spider_table = "jingqu_spider_table"
        self.jingdian_spider_table = "jingdian_spider_table"
        self.jingqu_mapping_table = "jingqu_mapping_table"

    def get(self, keyword=None, longitude=None, latitude=None, jingqu_id=None, province=None, city=None):
        flag = False
        jingdian_spider_table = self.db[self.jingdian_spider_table]
        jingqu_mapping_table = self.db[self.jingqu_mapping_table]
        jingqu_spider_table = self.db[self.jingqu_spider_table]
        items = []
        match = False
        if keyword:
            # 景区名称完全匹配
            condition = {"jingqu": keyword, "longitude": {"$exists": "true"}}
            if jingqu_mapping_table.find({"jingqu": keyword}).count() == 0:
                # 景区名称模糊匹配
                condition = {"jingqu": {'$regex': keyword}, "longitude": {"$exists": "true"}}
            else:
                match = True
        elif jingqu_id:
            condition = {"jingqu_id": jingqu_id, "longitude": {"$exists": "true"}}
        elif province and city and longitude and latitude:
            # 查找以当前位置为中心点距离为10KM以内的景区。
            condition = {"province": province, "city": city, "longitude": {"$exists": "true", "$gt": longitude - 0.1, "$lt": longitude + 0.1}, "latitude": {"$exists": "true", "$gt": latitude - 0.1, "$lt": latitude + 0.1}}
            if jingqu_mapping_table.find(condition).count() == 0:
                # 查找以当前位置为中心点距离为50KM以内的景区。
                condition = {"province": province, "city": city, "longitude": {"$exists": "true", "$gt": longitude - 0.5, "$lt": longitude + 0.5}, "latitude": {"$exists": "true", "$gt": latitude - 0.5, "$lt": latitude + 0.5}}
        try:
            for jingqu in jingqu_mapping_table.find(condition):
                item_jingqu = {}
                item_jingqu["jingqu_id"] = jingqu["jingqu_id"]
                item_jingqu["province"] = jingqu["province"]
                item_jingqu["city"] = jingqu["city"]
                item_jingqu["jingqu"] = jingqu["jingqu"]
                item_jingqu["longitude"] = jingqu["longitude"]
                item_jingqu["latitude"] = jingqu["latitude"]
                jingqu_id = jingqu["jingqu_id"]
                # 为了省流量，当用户自动搜索的时候，只返回景区的部分信息。
                if not keyword:
                    item_jingqu["jingdian"] = {}
                    item_jingqu["longitude"] = jingqu["longitude"]
                    item_jingqu["latitude"] = jingqu["latitude"]
                    for item in jingqu_spider_table.find({"jingqu_id": jingqu_id}):
                        item_jingqu[item["keyword"]] = item["description"]
                    for item in jingdian_spider_table.find({"jingqu_id":jingqu_id, "longitude": {"$exists": "true"}}):
                            item_jingqu["jingdian"][item["jingdian"]] = item["description"]
                            item_jingqu["jingdian"][item["longitude"]] = item["longitude"]
                            item_jingqu["jingdian"][item["latitude"]] = item["latitude"]
                items.append(item_jingqu)
        except ServerSelectionTimeoutError:
            return {"msg": "database cannot connected!", "code": 500}
        if len(items) > 0:
            if match and latitude:
                # 返回精确查找的所有景区并且按照当前经纬度的距离的远近排序
                return {"data": sorted(items, key=lambda x: self.calcDistance(latitude, longitude, x["latitude"], x["longitude"])), "msg": "成功", "code": 200}
            elif province and city and longitude and latitude:
                # 返回距离最近的一个景区
                return {"data": sorted(items, key=lambda x: self.calcDistance(latitude, longitude, x["latitude"], x["longitude"]))[0], "msg": "成功", "code": 200}
            else:
                # 返回模糊匹配的所有所有景区并且按照匹配的精确度排序
                return {"data": sorted(items, key=lambda x: len(x["jingqu"])), "msg": "成功", "code": 200}

        else:
            return {"msg": "没有查询到的景区！", "code": 200}

    def socket_jingqu_mapping(self, args):
        table = self.db[self.jingqu_mapping_table]
        keywords = map(lambda x: x, args)
        provinces_all = {}
        condition = {}
        if "province" in keywords:
            condition["province"] = args["province"]
        if "new" in keywords:
            condition["new"] = args["new"]
        for item in table.find(condition):
            if item["province"] not in provinces_all.keys():
                provinces_all[item["province"]] = {"id": "", "jingqu": {}}
                provinces_all[item["province"]]["id"] = item["id"]
            if int(item["jingqu_id"]) not in provinces_all[item["province"]]["jingqu"].keys():
                provinces_all[item["province"]]["jingqu"][int(item["jingqu_id"])] = item["jingqu"]
        return provinces_all

    def scenic_spot_spider(self, args=None):
        # print table
        # print args
        table = self.db[self.jingqu_spider_table]
        try:
            if args:
                keywords = map(lambda x: x, args)
                print keywords
                items = {}
                for keyword in keywords:
                    items[keyword] = args.get(keyword)
                items["jingqu_id"] = int(items["jingqu_id"])
                print items
                if table.find({"jingqu_id": items["jingqu_id"], "keyword": items["keyword"]}).count() > 0:
                    result_from_db = table.find({"jingqu_id": items["jingqu_id"], "keyword": items["keyword"]})[0]
                    if result_from_db["description"] != items["description"]:
                        print "start to update"
                        table.update(result_from_db, items)
                    else:
                        print "no need to update"
                else:
                    print "start to insert"
                    table.insert(items)
                jingqu_mapping_table = self.db[self.jingqu_mapping_table]
                if jingqu_mapping_table.find({"jingqu_id": items["jingqu_id"]}).count() > 0:
                    value_table_jingqu_mapping_table = jingqu_mapping_table.find({"jingqu_id": items["jingqu_id"]})[0]
                    if value_table_jingqu_mapping_table["new"] == "True":
                        value_table_jingqu_mapping_table["new"] = "False"
                        jingqu_mapping_table.update({"jingqu_id": value_table_jingqu_mapping_table["jingqu_id"]}, value_table_jingqu_mapping_table)
                return True
            else:
                return False
        except:
            return False

    def jingdian_spider(self, args=None):
        # print table
        # print args
        table = self.db[self.jingdian_spider_table]
        table.delete_many()
        try:
            if args:
                keywords = map(lambda x: x, args)
                print keywords
                items = {}
                for keyword in keywords:
                    items[keyword] = args.get(keyword)
                items["jingqu_id"] = int(items["jingqu_id"])
                print items
                if table.find({"jingqu_id": items["jingqu_id"], "jingdian": items["jingdian"]}).count() > 0:
                    print "OK"
                    result_from_db = table.find({"jingqu_id": items["jingqu_id"], "jingdian": items["jingdian"]})[0]
                    if result_from_db["description"] != items["description"]:
                        print "start to update"
                        table.update(result_from_db, items)
                    else:
                        print "no need to update"
                else:
                    print "start to insert"
                    table.insert(items)
                return True
            else:
                return False
        except:
            return False

    def calcDistance(self, Lat_A, Lng_A, Lat_B, Lng_B):
        Lng_B = Lng_B + 0.01
        ra = 6378.140  # 赤道半径 (km)
        rb = 6356.755  # 极半径 (km)
        flatten = (ra - rb) / ra  # 地球扁率
        rad_lat_A = radians(Lat_A)
        rad_lng_A = radians(Lng_A)
        rad_lat_B = radians(Lat_B)
        rad_lng_B = radians(Lng_B)
        pA = atan(rb / ra * tan(rad_lat_A))
        pB = atan(rb / ra * tan(rad_lat_B))
        xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
        c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
        c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
        dr = flatten / 8 * (c1 - c2)
        distance = ra * (xx + dr)
        return distance

# if __name__ == "__main__":
    # handle_database = HandleDatabase()
    # result =  handle_database.get(u"天台山")
    # print result
    # print json.dumps(result)
    # handle_database.socket_jingqu_mapping()

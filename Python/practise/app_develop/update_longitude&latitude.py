# -*- coding: utf-8 -*-
from pymongo import MongoClient
import urllib2
import sys


def get_location_info(item, old_city, url, table, try_again=False):
    print url
    contents = eval(urllib2.urlopen(url).read())
    print contents
    if contents["status"] == 0:
        if try_again:
            longitude = contents["results"][0]["location"]["lng"]
            print longitude
            latitude = contents["results"][0]["location"]["lat"]
            print latitude
        else:
            longitude = contents["result"]["location"]["lng"]
            print longitude
            latitude = contents["result"]["location"]["lat"]
            print latitude
        item["longitude"] = longitude
        item["latitude"] = latitude
        table.update({"province": item["province"], "city": old_city, "jingqu": item["jingqu"]}, item)
        print "update passed!"
        return True

client = MongoClient('127.0.0.1', 27017)
db = client['jingqu_db_test']
jingqu_mapping_table = db["jingqu_mapping_table"]
count = 0
flag = False
for item in jingqu_mapping_table.find():
    if "longitude" not in item.keys() and "latitude" not in item.keys():
        old_city = item["city"].encode("utf-8")
        city = item["city"].encode("utf-8").replace(" ", "20%")
        jingqu = item["jingqu"].encode("utf-8").split("[")[0].replace(" ", "20%")
        url = "http://api.map.baidu.com/geocoder/v2/?address=" + jingqu + "&output=json&ak=aYA41KlrKEisD16rgtMKVfoRhzrGPkbA&city=" + city
        try:
            if get_location_info(item, old_city, url, jingqu_mapping_table):
                count += 1
            else:
                a
        except:
            url = "http://api.map.baidu.com/place/v2/search?q=" + jingqu + "&region=" + city + "&output=json&ak=aYA41KlrKEisD16rgtMKVfoRhzrGPkbA&tag=旅游景点&page_size=1&page_num=0"
            try:
                if get_location_info(item, old_city, url, jingqu_mapping_table, try_again=True):
                    count += 1
                else:
                    a
            except:
                print "update failed!"
                pass
    if count == 20000:
        sys.exit(0)
print count

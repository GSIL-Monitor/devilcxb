# -*- coding: cp936 -*-
import urllib2
import re
from pymongo import MongoClient

contents = urllib2.urlopen("http://www.51yala.com/list/list_141_1.Html").read()
provinces = re.findall('<a href="(http://www.51yala.com/list/list_.*?\.[h-hH-H]tml)" target="_blank">(.*<)/a>', contents)
links = {}
domain = "http://www.51yala.com/"
org_provinces = [u"�Ϻ�", u"����", u"�㽭", u"����", u"����", u"���", u"�㶫", u"�ӱ�", u"����", u"ɽ��", u"����", u"����", u"����", u"����", u"�Ĵ�", u"����", u"����", u"ɽ��", u"����", u"����", u"������", u"����", u"����", u"����", u"����", u"����", u"�ຣ", u"����", u"�½�", u"����", u"����", u"���", u"����", u"̨��"]
for province in provinces:
    link = province[0]
    province = province[1][:-1].decode("gbk")
    #print province
    if province in org_provinces:
        links[province] = link
for key in links.keys():
    flag = False
    print key
    print links[key]
    try:
        contents = urllib2.urlopen(links[key]).read().decode("gbk")
    except UnicodeDecodeError:
        try:
            contents = urllib2.urlopen(links[key]).read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                contents = urllib2.urlopen(links[key]).read().decode("gb2312")
            except UnicodeDecodeError:
                contents = urllib2.urlopen(links[key]).read()
                more_info_link = domain + re.findall('a href="\.\./(list/list_.*?\.[h-hH-H]tml)"  target="_blank".*?</a>', contents)[0]
                flag = True
    if not flag:
        more_info_link = domain + re.findall('a href="\.\./(list/list_.*?\.[h-hH-H]tml)"  target="_blank".*?' + u"ȫ�����ξ���" + '</a>', contents)[0]
    links[key] = more_info_link

details = {}
for key in links.keys():
    print key
    print links[key]
    dict_jingdian = {}
    contents = urllib2.urlopen(links[key]).read().decode("gbk")
    #print re.findall('<a href="\.\./(Html/.*?\.html)" target=_blank>(.*?<)/a>', contents)
    for item in re.findall('<a href="\.\./([h-hH-H]tml/.*?\.[h-hH-H]tml)" target=_blank>(.*?<)/a>', contents):
        dict_jingdian[item[1][:-1]] = domain + item[0]
    details[key] = dict_jingdian
    print details[key]

client=MongoClient('127.0.0.1', 27017)
db = client['jingqu_db_test']
jingqu_mapping_table = db["jingqu_mapping_table"]

all_info = []
for item in jingqu_mapping_table.find():
    del item["_id"]
    del item["link"]
    all_info.append(item)

count = 1
for key in sorted(details.keys()):
    for jingqu in details[key].keys():
        link = details[key][jingqu]
        #print link
        try:
            contents = urllib2.urlopen(link).read()
            #print contents
            city = re.findall(".*>(.*)</a>", re.findall('<xoYu_CMS_CODE:NEWS:NEWS_TYPE>.*(<a href=.*?\.[h-hH-H]tml">.*?</a>).*(<a href=.*?\.[h-hH-H]tml">.*?</a>).*(<a href=.*?\.[h-hH-H]tml">.*?</a>).*</xoYu_CMS_CODE:NEWS:NEWS_TYPE>', contents)[0][-1])[0].decode("gbk")
            if {"province": key, "city": city, "jingqu": jingqu} not in all_info:
                jingqu_mapping_table.insert({"id":str(count), "province": key, "city": city, "jingqu": jingqu.split("[")[0], "link": details[key][jingqu], "new": "True"})
            else:
                print "no need to insert item"
        except urllib2.HTTPError:
            print link
            print jingqu
            print key
            print "link is not available"
        except IndexError:
            print link
            print jingqu
            print key
            print "city can not found"
        except urllib2.URLError:
            print link
            print jingqu
            print key
            print "try to open it again"
    count += 1

client.close()

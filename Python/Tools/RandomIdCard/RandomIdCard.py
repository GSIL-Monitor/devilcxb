# -*- coding:utf-8 -*-
import random, os
from datetime import date, timedelta


class RandomIdCard(object):
    def __init__(self):
        pass

    def getdistrictcode(self):
        with open(os.path.join(os.path.dirname(__file__), 'districtcode.txt')) as file:
            data = file.read()
        districtlist = data.split('\n')
        global codelist
        codelist = []
        for node in districtlist:
            # print node
            if node[10:11] != ' ':
                state = node[10:].strip()
            if node[10:11] == ' ' and node[12:13] != ' ':
                city = node[12:].strip()
            if node[10:11] == ' ' and node[12:13] == ' ':
                district = node[14:].strip()
                code = node[0:6]
                codelist.append({"state": state, "city": city, "district": district, "code": code})
        return codelist

    def gennerator(self, district=None):
        codelist = self.getdistrictcode()
        if district:
            for i in codelist:
                if i["district"].decode("gb2312") == district:
                    id = i
                    break
        else:
            id = codelist[random.randint(0, len(codelist) - 1)]
        id = id['code']  # 地区项
        id = id + str(random.randint(1930, 2013))  # 年份项
        da = date.today() + timedelta(days=random.randint(1, 366))  # 月份和日期项
        id = id + da.strftime('%m%d')
        id = id + str(random.randint(100, 300))  # ，顺序号简单处理

        i = 0
        count = 0
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
        checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '5', '9': '3',
                     '10': '2'}  # 校验码映射
        for i in range(0, len(id)):
            count = count + int(id[i]) * weight[i]
        id = id + checkcode[str(count % 11)]  # 算出校验码
        return id


if __name__ == '__main__':
    RandomIdCard = RandomIdCard()
    print """Idcard
-----"""
    print RandomIdCard.gennerator(district=u"东城区")
    print RandomIdCard.gennerator(district=u"东城区")
    print "-----"

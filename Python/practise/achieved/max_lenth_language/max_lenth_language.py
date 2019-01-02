# -*- coding: cp936 -*-
import xlrd
from collections import Counter

File = xlrd.open_workbook(r"D:\Project\UserCare\v1.7.0\多语言测试\UserCareV1.7.0_20160203.xlsx")
table = File.sheets()[0]
print len(table.col_values(0))
count = 1
flag = True
max_values = []
max_items = []
lanuages = table.row_values(0)[1:]
while flag:
    try:
        values = table.row_values(count)[1:]
        count += 1
        len_values = map(lambda x: len(x), values)
        # print max(len_values)
        max_values.append(len_values.index(max(len_values)))
        # print max_values
        max_items.append(values[len_values.index(max(len_values))])
        # print max_items
    except IndexError:
        flag = False

print max(map(lambda x: x[1], Counter(max_values).items()))
max_languages_location = filter(lambda x: x[1] == max(map(lambda y: y[1], Counter(max_values).items())),
                                Counter(max_values).items())
print max_languages_location
print filter(lambda x: lanuages.index(x) in map(lambda y: y[0], max_languages_location), lanuages)
for item in max_items:
    print item

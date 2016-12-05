import datetime
import time

d1 = datetime.datetime.now()
d1 = d1 + datetime.timedelta(days=1)

flag = True
while flag == True:
    d3 = d1 + datetime.timedelta(days=13)
    print str(d3).split()[0]
    d1 = d3 + datetime.timedelta(days=1)
    if "2017" in str(d3).split()[0]:
        flag = False

#time.strftime('%Y-%m-%d %H:%M:%S',d3)


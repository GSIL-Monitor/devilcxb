# -*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import re
import sys
import datetime
import os

print datetime.datetime.strptime("09:29", "%M:%S")

login_url = 'http://10.40.11.129:81/zentao/user-login.html'
login_data = {"account": "testCD",
              "password": "Aa123456"}
headers = {"Content-Type": "application/x-www-form-urlencoded",
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
           "referer": "http://10.1.10.42:81/zentao/my/"
           }

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
req = urllib2.Request(url=login_url, headers=headers)
urllib2.urlopen(req, data=urllib.urlencode(login_data)).read()
url = "http://10.40.11.129:81/zentao/project-dynamic-761-today--date_desc-8-100-1.html"
req = urllib2.Request(
    url="http://10.40.11.129:81/zentao/project-dynamic-%s-today--date_desc-8-100-1.html" % (os.environ.get("project_id")),
    headers=headers)
contents = urllib2.urlopen(req, data=urllib.urlencode(login_data)).read()
print contents
team = ["池小波", "张鑫", "荣嫒", "李勇锋", "张伟", "蔡昕宸"]
records = re.findall(
    "(\d+:\d+)</span>\n +?<span class=.*?>\n +?((?:%s)) 记录了工时" % (reduce(lambda x, y: x + "|" + y, team)), contents,
    re.S)
print records
for i in records:
    print i[0], i[1]
html = '<table border="1"><tr><th>已更新</th><th>未更新</th><tr><tr><td></td><td></td></tr></table>'
if records:
    updated_team = filter(lambda x: x in set(map(lambda x: x[1], filter(
        lambda x: datetime.datetime.strptime(x[0], "%M:%S") > datetime.datetime.strptime("17:00", "%M:%S"), records))),
                          team)
    if updated_team:
        records = filter(lambda x: x not in updated_team, team)
        if records:
            records = reduce(lambda x, y: x + "," + y, records)
        else:
            records = ""
        html = '<table border="1"><tr><th>已更新</th><th>未更新</th><tr><tr><td>%s</td><td>%s</td></tr></table>' % (
            reduce(lambda x, y: x + "," + y, updated_team), records)
print html
html = html.replace("\n", "<\ br>")
print html
# File = open("params.txt", "w")
# File.write(
#     "recipientList=cc:chixiaobo@lixin360.com\n")
# File.write("title=今天更新任务情况\n")
# File.write("contents=%s" % (html))
# File.close()

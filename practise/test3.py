# -*- coding: utf-8 -*-
import jenkinsapi.jenkins as jenkins
import urllib2
import urllib
import json
import cookielib


"""
jenkins_server = 'http://172.26.32.18/jenkins/'
Username = "xiaobo.chi"
Password = "DEVIL_cxb1"
job_name = "test"
server = jenkins.Jenkins(jenkins_server, username=Username, password=Password)
params = {"test_Node": "CD_VAL55_9998"}
server.build_job(job_name, params)
"""
autherization_info = {"j_username": "xiaobo.chi", "j_password": "DEVIL_cxb1", "Submit": "登录", "from": ""}
# url = "http://172.26.32.18/jenkins/j_acegi_security_check?j_username=xiaobo.chi&j_password=DEVIL_cxb1&Submit=登录"
data = urllib.urlencode(autherization_info)
# print urllib2.urlopen(url, data).read()
url = "http://172.26.32.18/jenkins/j_acegi_security_check"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
           "Content-Type": "application/x-www-form-urlencoded"
           }
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
# urllib2.install_opener(opener)
req = urllib2.Request(url, data=data, headers=headers)
opener.open(req).read()
urllib2.install_opener(opener)
build_url = "http://172.26.32.18/jenkins/view/VAL_Test/job/test/buildWithParameters?delay=0sec"
json_data = {"parameter":[{"name": "abcd", "value": "CD_VAL55_9998"}], "Submit": "开始构建"}
data = {
    "Submit": "开始构建",
    "testSring": "test"
}
req = urllib2.Request(build_url, headers)
print opener.open(req, json.dumps(json_data)).read()

# -*- coding: utf-8 -*-
from getCookie import GetCookie
from post import Post
from get import Get
import json


GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/login.html", {"username_element_id_name": ["email", "usercare@tcl.com"], "password_element_id_name": ["password", "test"], "confirm_button_class_name": "btn-primary"}, "http://usercare-tcl-test.tclclouds.com/boss")
cookie = GetCookie.generateCookie()
GetCookie.close_driver()

headers = {'Cookie': cookie,
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0",
           'Content-Type': "application/json"
           }

Post = Post()
Get = Get()
# 接口一
url = "http://usercare-tcl-test.tclclouds.com/boss/banner/save.json"
data = {"name": "testsave222", "imageUrl": "http://ep.tclcom.com/_layouts/TCL.EP.GPortal.UI/images/logo.png", "contentUrl": "www.github1.com"}
#data = urllib.urlencode(data)
data = json.dumps(data)
print data
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")

# 接口二
url = "http://usercare-tcl-test.tclclouds.com/boss/banner/update.json"
data = {"id": "38", "name": "testsave2222", "imageUrl": "http://ep.tclcom.com/_layouts/TCL.EP.GPortal.UI/images/logo.png", "contentUrl": "www.github1.com"}
data = json.dumps(data)
#data = urllib.urlencode(data)
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")

# 接口三
url = "http://usercare-tcl-test.tclclouds.com/api/problemReports/save.json"
data = {"issue": "test", "description": "test222", "sFrom": "common", "user_account": "test", "language": "chinese", "model": "ALCATEL ONE TOUCH 7040A"}
data = json.dumps(data)
#data = urllib.urlencode(data)
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "code")

# 接口四
url = "http://usercare-tcl-test.tclclouds.com/api/suggestion/save.json"
data = {"issue": "test", "description": "test222", "sFrom": "common", "user_account": "test", "language": "chinese", "model": "ALCATEL ONE TOUCH 7040A"}
data = json.dumps(data)
#data = urllib.urlencode(data)
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "code")

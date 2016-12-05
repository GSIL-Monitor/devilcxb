# -*- coding: utf-8 -*-
from GetCookie import GetCookie
from Post import Post
from Get import Get
import json

"""
GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/login.html", {"username_element_id_name": ["email", "usercare@tcl.com"], "password_element_id_name": ["password", "test"], "confirm_button_class_name": "btn-primary"}, "http://usercare-tcl-test.tclclouds.com/boss")
cookie = GetCookie.generateCookie()
GetCookie.close_driver()
"""
headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0",
           'Content-Type': "application/json"
           }

Post = Post()
Get = Get()
# 接口一
url = "http://10.115.101.239:5001/sso/user.action"
data = {"op":"Login.login","email":"jenkins@tcl.com","pwd":"Aa123456"}
import urllib
json_data = Post.post_url_and_get_result(url, data=json.dumps(data), headers=headers)
print json_data["data"]["sid"]
"""
data = {"name": "testsave222", "imageUrl": "http://ep.tclcom.com/_layouts/TCL.EP.GPortal.UI/images/logo.png", "contentUrl": "www.github1.com"}
#data = urllib.urlencode(data)
data = json.dumps(data)
print data
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")

# update.json
data = {"id": "38", "name": "testsave2222", "imageUrl": "http://ep.tclcom.com/_layouts/TCL.EP.GPortal.UI/images/logo.png", "contentUrl": "www.github1.com"}
data = json.dumps(data)
#data = urllib.urlencode(data)
json_data = Post.post_url_and_get_result(url, data, headers)
print json_data
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")
"""
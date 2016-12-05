# -*- coding: utf-8 -*-
from GetCookie import GetCookie
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"}
GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/admin/login", {"username_element_id_name": ["email", "chunlan.hu@tcl.com"], "password_element_id_name": ["password", "4ufkr1nd"]}, headers, "http://tstream-test.tclclouds.com/cms/static/index.html")
cookie = GetCookie.generateCookie()

from UploadFile_post import UploadFile_post
from Get import Get
Get = Get()
UploadFile_post = UploadFile_post()
url = "http://tstream-test.tclclouds.com/cms/apk/add"
data = {"versionCode": 10, "versionName": "test", "description": "test", "appName": "test"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0", "Cookie": cookie}
print Get.get_json_result("http://tstream-test.tclclouds.com/cms/apk/list", headers=headers)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0", "Cookie": cookie}
print UploadFile_post.get_upload_result(url, r"C:\Users\xiaobo.chi\Desktop\SpacePlus.apk", "uploadFile", data, headers)

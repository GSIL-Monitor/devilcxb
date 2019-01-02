#coding: utf-8  
from UploadFile_post import UploadFile_post
from GetCookie import GetCookie
import urllib
import json


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"}
cookie = GetCookie("http://10.115.101.231:50000/login", {"username_element_id_name": ["loginId", "test@tcl.com"], "password_element_id_name": ["password", "123"]}, headers, "http://10.115.101.231:50000/index")
print cookie.generateCookie()
headers["Cookie"] = cookie.generateCookie()
UploadFile_post = UploadFile_post()
print UploadFile_post.get_upload_result("http://10.115.101.231:50000/upload", "test.txt", "file", headers_passed=headers, return_result=False, filename="test.txt", selection_choice_list={"devicenos": ["2440fc", "36c4ee", "2b01db"]})
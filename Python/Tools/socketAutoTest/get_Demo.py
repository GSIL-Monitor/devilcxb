# -*- coding: utf-8 -*-
from GetCookie import GetCookie
from Get import Get

GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/login.html", {"username_element_id_name": ["email", "usercare@tcl.com"], "password_element_id_name": ["password", "test"], "confirm_button_class_name": "btn-primary"}, "http://usercare-tcl-test.tclclouds.com/boss")
#GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/login.html", {"username_element_id_name": ["email", "usercare@tcl.com"], "password_element_id_name": ["password", "test"], "confirm_button_class_name": ["btn-primary"]}, "http://usercare-tcl-test.tclclouds.com/boss")
cookie = GetCookie.generateCookie()
GetCookie.close_driver()

headers = {'Cookie': cookie,
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0",
           'Content-Type': "application/json"
           }
Get = Get()
# 接口1
url = "http://usercare-tcl-test.tclclouds.com/boss/banner/list.json"
data = {}
json_data = Get.get_json_result(url, data=None, headers=headers)
# 获取所有的json数据
print json_data
# 获取msg字段的值
print Get.get_keyword_result(json_data, "msg")
# 获取json的主体items里面name字段的所有值
print Get.get_keyword_results(json_data, "items", "name")
# 获取json数据里面所有的字段
print Get.get_all_keywords(json_data, keywords=[])
# 获取数据主体items的字段
print Get.get_data_label_keywords(json_data, "items")
# 获取数据主体items的所有字段
keywords_for_data_label =  Get.get_data_label_keywords(json_data, "items", keywords=[], all=True)
print keywords_for_data_label
# 比较所有主体items的所有字段
# print Get.compare_all_keywords_for_data_label(keywords_for_data_label)
# 获取主体items的index值值。
print Get.get_result_for_data_label("items", json_data, index=-1)
# 获取主体items的所有值，返回为一个list.
print Get.get_all_results_for_data_label("items", json_data)

# 接口2
url = "http://usercare-tcl-test.tclclouds.com/boss/feedback/list.json"
print Get.get_keyword_result(json_data, "msg")
# 获取json的主体items里面name字段的所有值
print Get.get_keyword_results(json_data, "items", "name")
# 获取json数据里面所有的字段
print Get.get_all_keywords(json_data, keywords=[])
# 获取数据主体items的字段
print Get.get_data_label_keywords(json_data, "items")
# 获取数据主体items的所有字段
keywords_for_data_label =  Get.get_data_label_keywords(json_data, "items", keywords=[], all=True)
print keywords_for_data_label
# 比较所有主体items的所有字段
# print Get.compare_all_keywords_for_data_label(keywords_for_data_label)
# 获取主体items的index值值。
print Get.get_result_for_data_label("items", json_data, index=-1)
# 获取主体items的所有值，返回为一个list.
print Get.get_all_results_for_data_label("items", json_data)
# 测试页数和数据数量
pages = Get.get_json_result(url, headers=headers)["pages"]
total_num = Get.get_json_result(url, headers=headers)["total"]
max_page_number, total_number = Get.get_max_pages(url,"items", "pageNum", data = None, headers = headers, default_per_page=10)
print pages, max_page_number
print total_num, total_number
# 测试分页
print Get.per_page_test(3, url, "items", "pageNum", "pageSize",  max_page_number, total_number, data = None, headers = headers, default_per_page=10)

# 接口三
url = "http://usercare-tcl-test.tclclouds.com/boss/feedback/getModel.json"
json_data = Get.get_json_result(url, headers=headers)
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")
print Get.get_all_keywords(json_data,keywords=[])
print Get.get_all_results_for_data_label("item", json_data)

# 接口四
url = "http://usercare-tcl-test.tclclouds.com/boss/banner/delete.json"
data = {"bannerId": 55}
json_data = Get.get_json_result(url, data=data, headers=headers)
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")
#print Get.get_all_keywords(json_data,keywords=[])
#print Get.get_all_results_for_data_label("item", json_data)

# 接口五
url = "http://usercare-tcl-test.tclclouds.com/boss/banner/editStatus.json"
data = {"bannerId": 33, "status": "N"}
json_data = Get.get_json_result(url, data=data, headers=headers)
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")
data = {"bannerId": 33, "status": "Y"}
json_data = Get.get_json_result(url, data=data, headers=headers)
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")
data = {"bannerId": 55, "status": "Y"}
json_data = Get.get_json_result(url, data=data, headers=headers)
print Get.get_keyword_result(json_data, "msg")
print Get.get_keyword_result(json_data, "status")

# 接口六
url = "http://usercare-tcl-test.tclclouds.com/api/banner/data.json"
data = {}
json_data = Get.get_json_result(url, data=None)
# 获取所有的json数据
print json_data
# 获取msg字段的值
print Get.get_keyword_result(json_data, "msg")
# 获取json的主体items里面name字段的所有值
print Get.get_keyword_results(json_data, "data", "link")
# 获取json数据里面所有的字段
print Get.get_all_keywords(json_data, keywords=[])
# 获取数据主体items的字段
print Get.get_data_label_keywords(json_data, "data")
# 获取数据主体items的所有字段
keywords_for_data_label =  Get.get_data_label_keywords(json_data, "data", keywords=[], all=True)
print keywords_for_data_label
# 比较所有主体items的所有字段
# print Get.compare_all_keywords_for_data_label(keywords_for_data_label)
# 获取主体items的index值值。
print Get.get_result_for_data_label("data", json_data, index=-1)
# 获取主体items的所有值，返回为一个list.
print Get.get_all_results_for_data_label("data", json_data)
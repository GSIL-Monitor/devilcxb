# -*- coding: utf-8 -*-
from selenium import webdriver
from exceptions import *
import time


class GetCookie(object):
    # 是否需要跳转过后的第二个url的Cookie,如果不需要请忽略url2的参数
    # authorization_info的数据格式为{"username_element_id_name": [id_name, username], "password_element_id_name": [id_name,password], "confirm_button_class_name":class_name}
    def __init__(self, url1, authorization_info, url2=None):
        self.url1 = url1
        self.url2 = url2
        self.authorization_info = authorization_info
        if sorted(self.authorization_info.keys()) != sorted(["username_element_id_name", "password_element_id_name", "confirm_button_class_name"]):
            if len(filter(lambda x: x not in ["username_element_id_name", "password_element_id_name", "confirm_button_class_name"], self.authorization_info.keys())) == 0:
                raise raiseExceptions(str(filter(lambda x: x not in self.authorization_info.keys(), ["username_element_id_name", "password_element_id_name", "confirm_button_class_name"])) + " is missed!")
            else:
                raise raiseExceptions(str(filter(lambda x: x not in ["username_element_id_name", "password_element_id_name", "confirm_button_class_name"], self.authorization_info.keys())) + " is more than defined!!")
        else:
            if len(self.authorization_info["username_element_id_name"]) != 2 or len(self.authorization_info["password_element_id_name"]) != 2 or type(self.authorization_info["confirm_button_class_name"]) != str:
                raise raiseExceptions('the amount of values for authorization_info is wrong, please according to {"username_element_id_name": [id_name, username], "password_element_id_name": [id_name,password], "confirm_button_class_name":class_name}')
        self.driver = webdriver.Firefox()

    # 需要用火狐浏览器获取cookie
    def generateCookie(self):
        try:
            self.driver.get(self.url1)
            self.driver.find_element_by_id(self.authorization_info["username_element_id_name"][0]).send_keys(self.authorization_info["username_element_id_name"][1])
            self.driver.find_element_by_id(self.authorization_info["password_element_id_name"][0]).send_keys(self.authorization_info["password_element_id_name"][1])
            self.driver.find_element_by_class_name(self.authorization_info["confirm_button_class_name"]).click()
            time.sleep(2)
            if self.url2:
                self.driver.get("http://usercare-tcl-test.tclclouds.com/boss")
            time.sleep(2)
            cookie= self.driver.get_cookies()
            return cookie[0]['name'] + "=" + cookie[0]['value']
        except:
            self.close_driver()

    # 关闭浏览器
    def close_driver(self):
        self.driver.close()
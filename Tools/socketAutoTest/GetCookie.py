# -*- coding: utf-8 -*-
import urllib2
import urllib
import cookielib
import re
import logging
logging.basicConfig(level=logging.INFO)

class GetCookie(object):
    def __init__(self, url1, authorization_info, headers, url2=None):
        """
        初始化获取Cookie
        :param url1: 在TCL的CMS认证中，一般都是通过认证中心做认证, 所以这种情况下需要传入待测试的CMS主页地址做为url2的参数来获取实际的Cookie
        :param authorization_info: 认证信息，格式为{"username_element_id_name": [id_name, username], "password_element_id_name": [id_name,password]}
        :param headers: 如要用到的头文件， 一般传入User-Agent即可
        :param url2: 待测的CMS地址主页，如果不通过认证中心做认证的，可以不传入url2
        :return:
        """
        self.url2 = url2
        self.cj =  cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.headers = headers
        if type(authorization_info) == unicode:
            authorization_info = eval(authorization_info)
        if sorted(authorization_info.keys()) != sorted(
                ["username_element_id_name", "password_element_id_name"]):
            if len(filter(lambda x: x not in ["username_element_id_name", "password_element_id_name",
                                              ], authorization_info.keys())) == 0:
                logging.error(str(filter(lambda x: x not in authorization_info.keys(),
                                                 ["username_element_id_name", "password_element_id_name"
                                                  ])) + " is missed!")
            else:
                logging.error(str(filter(
                    lambda x: x not in ["username_element_id_name", "password_element_id_name",
                                        ],
                    authorization_info.keys())) + " is more than defined!!")
        else:
            if len(authorization_info["username_element_id_name"]) != 2 or len(
                    authorization_info["password_element_id_name"]) != 2:
                logging.error(
                    'the amount of values for authorization_info is wrong, please according to {"username_element_id_name": [id_name, username], "password_element_id_name": [id_name,password]}')
        data = {}
        data[authorization_info["username_element_id_name"][0]] = authorization_info["username_element_id_name"][1]
        data[authorization_info["password_element_id_name"][0]] = authorization_info["password_element_id_name"][1]
        req = urllib2.Request(url1, data=urllib.urlencode(data), headers=self.headers)
        self.opener.open(req).read()
        self.match_url = url1

    # 需要用火狐浏览器获取cookie
    def generateCookie(self):
        """
        获取Cookie
        :return: Cookie
        """
        if self.url2:
            print self.url2
            self.match_url = self.url2
            req = urllib2.Request(self.url2, headers=self.headers)
            self.opener.open(req).read()
        for i in self.cj:
            # 一般情况下获取到的Cookie对应的域名的最后一位是/, 所以为了便于匹配，直接去掉最后一位
            if re.findall("<Cookie (.*) for (.*)>", str(i))[0][1][:-1] in self.match_url:
                logging.info("Cookie: " + re.findall("<Cookie (.*) for (.*)>", str(i))[0][0])
                return re.findall("<Cookie (.*) for (.*)>", str(i))[0][0]

if __name__ == "__main__":
    headers= {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"}
    GetCookie = GetCookie("http://passporttest.tclclouds.com/passport/admin/login", {"username_element_id_name": ["email", "usercare@tcl.com"], "password_element_id_name": ["password", "test"]}, headers, "http://usercare-tcl-test.tclclouds.com/boss/")
    print GetCookie.generateCookie()

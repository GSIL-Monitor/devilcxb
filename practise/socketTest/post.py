# -*- coding: utf-8 -*-
import urllib2
from exceptions import *


class Post(object):
    def __init__(self):
        pass

    # url: 测试的url
    # data: url请求时发送的数据
    # headers: url请求时发送的消息头
    # 功能：post url并且获取json格式的数据
    def post_url_and_get_result(self, url, data=None, headers=None):
        if headers:
            req = urllib2.Request(url, headers=headers)
        else:
            req = urllib2.Request(url)
        content = eval(urllib2.urlopen(req, data=data).read())
        if type(content) == dict:
            return content
        else:
            raise raiseExceptions("content is not json!\n" + content)
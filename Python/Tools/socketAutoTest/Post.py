# -*- coding: utf-8 -*-
import urllib2
from raiseExceptions import *
import json
import ssl


class Post(object):
    def __init__(self):
        pass

    # url: 测试的url
    # data: url请求时发送的数据
    # headers: url请求时发送的消息头
    # ssl_connection: 是否为https的连接方式
    # 功能：post url并且获取json格式的数据
    def post_url_and_get_result(self, url, data=None, headers=None, ssl_connection=False):
        if headers:
            req = urllib2.Request(url, headers=headers)
        else:
            req = urllib2.Request(url)
        if ssl_connection:
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            # context = ssl._create_unverified_context()
            content = eval(urllib2.urlopen(req, data=data, context=gcontext).read())
        else:
            content = eval(urllib2.urlopen(req, data=data).read())
        if type(content) == dict:
            return content
        else:
            raise raiseExceptions("content is not json!\n" + content)

    def convert_dict_to_json(self, data):
        """
        转换字典类型的数据为json格式
        """
        return json.dumps(data)
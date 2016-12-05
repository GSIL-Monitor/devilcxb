# -*- coding: utf-8 -*-
# test_client.py
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import poster.streaminghttp as streaminghttp
import urllib2
import urllib
import logging
import sys
logging.basicConfig(level=logging.INFO)

class UploadFile_post(object):
    def __init__(self):
        pass

    def get_upload_result(self, url, filepath, parametername, data=None, headers_passed=None, return_result=True, filename=None,selection_choice_list=None, ssl_connection=False):
        """
        此方法用于上传文件并且或者返回结果
        :param url: 请求的URL
        :param filepath: 请求的文件的绝对路径
        :param parametername: 上传文件接口定义的参数名称
        :param return_result: 是否返回测试结果
        :param filename: 文件名称，上传时显示的文件名称，请不要随意填写
        :param data: 需要传递请求参数
        :param headers_passed: 需要加入的请求头文件内容, 这个地方一定不要加入Content-Type的字段，否则会覆盖自动获取的headers
        :param selection_choice_list: 需要传递额外的参数例如{"devicenos": ["2440fc","36c4ee", "2b01db"]}
        :return: 返回上传文件的json result
        """
        if headers_passed:
            if "Content-Type" in headers_passed.keys():
                logging.error("Content-Type is no needed since it will be generated automatically via the framework!")
                sys.exit(1)

        # 在 urllib2 上注册 http 流处理句柄
        from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler
        handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler]
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)

        # headers 包含必须的 Content-Type 和 Content-Length
        # datagen 是一个生成器对象，返回编码过后的参数
        items = []
        if selection_choice_list:
            for key in selection_choice_list.keys():
                if type(selection_choice_list[key]) == dict or type(selection_choice_list[key]) == list:
                    for item in selection_choice_list[selection_choice_list.keys()[0]]:
                        items.append(MultipartParam(selection_choice_list.keys()[0], item))
                else:
                    items.append(MultipartParam(key, selection_choice_list[key]))
            if filename:
                pass
            else:
                filename=filepath.replace("/", "\\").split("\\")[-1]
            items.append(MultipartParam(parametername, filename=filename, fileobj=open(filepath, "rb")))
            datagen, headers = multipart_encode(items)
        else:
            datagen, headers = multipart_encode({parametername: open(filepath, "rb")})

        datagen = reduce(lambda x, y: x + y, map(lambda x: x, datagen))
        print datagen

        # 创建请求对象
        if data:
            data = urllib.urlencode(data)
            if "?" not in url:
                url = url + "?" + data
            else:
                url = url + "&" + data
        # print url
        # print datagen
        request = urllib2.Request(url, datagen, headers)
        if headers_passed:
            for header in headers_passed:
                request.add_header(header, headers_passed[header])
        # 实际执行请求并取得返回
        gcontext = None
        if ssl_connection:
            import ssl
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        if return_result:
            return eval(urllib2.urlopen(request, context=gcontext).read())
        else:
            urllib2.urlopen(request, context=gcontext).read()

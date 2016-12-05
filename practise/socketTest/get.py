# -*- coding: utf-8 -*-
import urllib
import urllib2
from exceptions import *
import random

class Get(object):
    def __init(self):
        pass

    # url: 测试的url
    # data: url请求时发送的数据
    # headers: url请求时发送的消息头
    # 功能：获取json格式的数据
    def get_json_result(self, url, data=None, headers=None):
        if data:
            data = urllib.urlencode(data)
            if "?" not in url:
                url = url + "?"
            url = url + data
        if headers:
            req = urllib2.Request(url, headers=headers)
        else:
            req = urllib2.Request(url)
        content = eval(urllib2.urlopen(req).read())
        if type(content) == dict:
            return content
        else:
            raise raiseExceptions("content is not json!\n" + content)

    # json_data: 字典格式的json数据
    # keywords: json数据里面的关键字，不一定是items里面字段，可以是外层的，如msg,status；如果是items里面的字段，会返回第一条数据里面这个字段的值
    # 功能：获取指定关键字的值
    def get_keyword_result(self, json_data, keyword):
        if keyword in json_data.keys():
            return json_data[keyword]
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    if self.get_keyword_result(json_data[key], keyword):
                        return json_data[key][keyword]
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        if self.get_keyword_result(item, keyword):
                            return item[keyword]
                            # break
        raise raiseExceptions("keyword " + keyword + " is not found!")

    # json_data: 字典格式的json数据
    # data_label: 数据的标签， 如items
    # keywords: json数据里面items字段里面的某一个字段
    # 功能：获取指定关键字的所有值，例如items里面name字段的所有值
    def get_keyword_results(self, json_data, data_label, keyword):
        if data_label in json_data.keys():
            values = []
            for item in json_data[data_label]:
                values.append(item[keyword])
            return values
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    if self.get_keyword_results(json_data[key], data_label, keyword):
                        return self.get_keyword_results(json_data[key], data_label, keyword)
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        if self.get_keyword_results(item, data_label, keyword):
                            return self.get_keyword_results(item, data_label, keyword)
                            # break
        raise raiseExceptions("keyword or data label is not found!")

    # json_data: 字典格式的json数据
    # keywords: 可以不传递这个参数，只作为第一次赋值的时候使用;在测试接口的时候第二个接口调用的时候需要传递[]座位初始值
    # 功能: 返回json数据里面所有的关键字，包含嵌套的
    def get_all_keywords(self,json_data, keywords=[]):
        keywords += json_data.keys()
        for key in json_data.keys():
            if type(json_data[key]) == dict:
                self.get_all_keywords(json_data[key], keywords)
            elif type(json_data[key]) == list:
                for item in json_data[key]:
                    if type(item) == dict:
                        self.get_all_keywords(item, keywords)
                        break
        return keywords

    # data_label: 数据的标签， 如items
    # json_data: 字典格式的json数据
    # keywords: 不需要传递这个参数，只作为第一次赋值的时候使用
    # all: True的时候返回所有的data_label数据的关键字，如items对应的所有数据的关键字，格式为[[], [], []];False的时候只返回data_label数据的第一个数据的所有关键字，如items对应的第一条数据的所有关键字，格式为[]
    # 功能：返回items字段的所有数据的关键字或者只返回一条数据的关键字
    def get_data_label_keywords(self, json_data, data_label, keywords=[], all=False):
        if data_label in json_data.keys():
            if type(json_data[data_label]) == dict:
                if all:
                    keywords.append(json_data[data_label].keys())
                else:
                    keywords += json_data[data_label].keys()
            elif type(json_data[data_label]) == list:
                for item in json_data[data_label]:
                    if all:
                        keywords.append(item.keys())
                    else:
                        keywords += item.keys()
                        break
            return keywords
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    if all:
                        keywords = self.get_data_label_keywords(json_data[key], data_label, all=True)
                    else:
                        keywords = self.get_data_label_keywords(json_data[key], data_label)
                    if keywords:
                        return keywords
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        if all:
                            keywords = self.get_data_label_keywords(item, data_label, all=True)
                        else:
                            keywords = self.get_data_label_keywords(item, data_label)
                        if keywords:
                            return keywords
                            # break
        raise raiseExceptions("data label is not found!")

    # lists: 所有数据的关键字的集合，如items字段对应的所有数据的关键字的集合
    # 功能：对比所有的关键字集合是不是一样
    def compare_all_keywords_for_data_label(self, lists):
        if lists.count(lists[0]) == len(lists):
            return True
        else:
            raise raiseExceptions("the keywords for data label is not the same!")

    # data_label: 数据的标签， 如items
    # json_data: 字典格式的json数据
    # index: 需要查找的数据的索引，默认值0代表查找第一个数据
    # 功能：返回指定的index的items里面的数据
    def get_result_for_data_label(self, data_label, json_data, index=0):
        if data_label in json_data.keys():
            if type(json_data[data_label]) == dict:
                return json_data[data_label]
            elif type(json_data[data_label]) == list:
                return json_data[data_label][index]
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    data = self.get_result_for_data_label(data_label, json_data[key], index)
                    if data:
                        return data
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        data = self.get_result_for_data_label(data_label, item, index)
                        if data:
                            return data
                            # break
        raise raiseExceptions("data label is not found!")

    # data_label: 数据的标签， 如items
    # json_data: 字典格式的json数据
    # 功能：返回items的所有数据
    def get_all_results_for_data_label(self, data_label, json_data):
        if data_label in json_data.keys():
            return json_data[data_label]
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    data = self.get_all_results_for_data_label(data_label, json_data[key])
                    if data:
                        return data
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        if type(item) == dict:
                            data = self.get_all_results_for_data_label(data_label, item)
                            if data:
                                return data
                                # break
        raise raiseExceptions("data label is not found!")

    # url: 测试的url
    # data_label: 数据的标签， 如items
    # page_keyword: 页数的关键字，如pageNum
    # data: url请求时发送的数据
    # headers: url请求时发送的消息头
    # default_per_page: 每一页默认的数据数量
    # 获取最大的页数和数据的总量，可以单独调用这个函数测试json数据里面的页数和数据总量是不是正确
    def get_max_pages(self, url, data_label, page_keyword, data=None, headers=None, default_per_page=10):
        flag = True
        page_number = 1
        total_number = 0
        while flag:
            if not data:
                data = {}
            data[page_keyword] = str(page_number)
            json_data = self.get_json_result(url, data, headers)
            amount_of_data = len(self.get_all_results_for_data_label(data_label, json_data))
            total_number += amount_of_data
            if amount_of_data == default_per_page:
                page_number += 1
            elif amount_of_data == 0:
                flag = False
                page_number -= 1
            else:
                flag = False
        # total_number = default_per_page*(page_number-1) + amount_of_data_for_last_page
        return page_number, total_number

    # times: 测试的次数
    # url: 测试的url
    # data_label: 数据的标签， 如items
    # page_keyword: 页数的关键字，如pageNum
    # per_page_keyword: 每一页显示多少数据的关键字，如pageSize
    # max_page_number:总页数; 如果接口测试的时候已经通过get_max_pages参数获取过值以后，可以直接传进来，而不用通过当前函数再次获取
    # total_number:数据总数; 如果接口测试的时候已经通过get_max_pages参数获取过值以后，可以直接传进来，而不用通过当前函数再次获取
    # data: url请求时发送的数据
    # headers: url请求时发送的消息头
    # default_per_page: 每一页默认的数据数量
    # 功能：如果接口里面有定义页数和每页显示的数据条数，可以调用这个函数进行测试,测试成功返回为True, 返回失败为False
    def per_page_test(self, times, url, data_label, page_keyword, per_page_keyword, max_page_number=None, total_number=None, data=None, headers=None, default_per_page=10):
        count = 0
        passed_times = 0
        if not max_page_number and not total_number:
            max_page_number, total_number = self.get_max_pages(url, data_label, page_keyword, data, headers, default_per_page)
        while count < times:
            page_number = random.choice(range(1, max_page_number))
            default_per_page = random.choice(range(1, total_number))
            if page_number*default_per_page < total_number:
                print page_number
                print default_per_page
                if not data:
                    data = {}
                data[page_keyword] = str(page_number)
                data[per_page_keyword] = str(default_per_page)
                json_data = self.get_json_result(url, data, headers)
                amount_of_data = len(self.get_all_results_for_data_label(data_label, json_data))
                if amount_of_data == default_per_page:
                    passed_times += 1
                count += 1
        if passed_times == times:
            return True
        else:
            return False
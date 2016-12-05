# -*- coding: utf-8 -*-
import urllib
import urllib2
from raiseExceptions import *
import random
import collections
from random import Random
import ssl

class Get(object):
    def __init(self):
        pass

    def get_json_result(self, url, data=None, headers=None, ssl_connection=False):
        """
        # url: 测试的url
        # data: url请求时发送的数据
        # headers: url请求时发送的消息头
        # ssl_connection: 是否为https的连接方式
        # 功能：获取json格式的数据
        """
        if data:
            data = urllib.urlencode(data)
            if "?" not in url:
                url = url + "?"
            url = url + data
        if headers:
            if type(headers) == unicode:
                headers = eval(headers)
            req = urllib2.Request(url, headers=headers)
        else:
            req = urllib2.Request(url)
        if ssl_connection:
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            # context = ssl._create_unverified_context()
            content = eval(urllib2.urlopen(req, context=gcontext).read())
        else:
            content = eval(urllib2.urlopen(req).read())
        if type(content) == dict:
            return content
        else:
            raise raiseExceptions("content is not json!\n" + content)

    def get_keyword_result(self, json_data, keyword):
        """
        # json_data: 字典格式的json数据
        # keywords: json数据里面的关键字，不一定是items里面字段，可以是外层的，如msg,status；如果是items里面的字段，会返回第一条数据里面这个字段的值
        # 功能：获取指定关键字的值
        """
        if keyword in json_data.keys():
            return json_data[keyword]
        else:
            for key in json_data.keys():
                if type(json_data[key]) == dict:
                    return_result = self.get_keyword_result(json_data[key], keyword)
                    if return_result or (return_result != False and return_result != None) or return_result == 0:
                        return return_result
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        return_result = self.get_keyword_result(item, keyword)
                        if return_result or (return_result != False and return_result != None) or return_result == 0:
                            return return_result
                            # break
        raise raiseExceptions("keyword " + keyword + " is not found!")

    def get_keyword_results(self, json_data, data_label, keyword):
        """
        # json_data: 字典格式的json数据
        # data_label: 数据的标签， 如items
        # keywords: json数据里面items字段里面的某一个字段
        # 功能：获取指定关键字的所有值，例如items里面name字段的所有值
        """
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

    def return_value(self,keyword):
        return keyword

    def get_all_keywords(self,json_data, keywords=[]):
        """
        # json_data: 字典格式的json数据
        # keywords: 可以不传递这个参数，只作为第一次赋值的时候使用;在测试接口的时候第二个接口调用的时候需要传递[]座位初始值
        # 功能: 返回json数据里面所有的关键字，包含嵌套的
        """
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

    def get_data_label_keywords(self, json_data, data_label, used_once=True, keywords=[], all=False):
        """
        # data_label: 数据的标签， 如items
        # json_data: 字典格式的json数据
        # used_once: 第一次调用的时候，可以不设置此参数，第二次或者重复调用是，used_once请设置为False
        # keywords: 不用设置这个参数，keyword只做内部逻辑使用
        # all: True的时候返回所有的data_label数据的关键字，如items对应的所有数据的关键字，格式为[[], [], []];False的时候只返回data_label数据的第一个数据的所有关键字，如items对应的第一条数据的所有关键字，格式为[]
        # 功能：返回items字段的所有数据的关键字或者只返回一条数据的关键字
        """
        if used_once:
            pass
        else:
            keywords = []
            used_once = True
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
                        keywords = self.get_data_label_keywords(json_data[key], data_label, used_once, keywords, all=True)
                    else:
                        keywords = self.get_data_label_keywords(json_data[key], data_label, used_once, keywords)
                    if keywords:
                        return keywords
                        # break
                elif type(json_data[key]) == list:
                    for item in json_data[key]:
                        if all:
                            keywords = self.get_data_label_keywords(item, data_label, used_once, keywords, all=True)
                        else:
                            keywords = self.get_data_label_keywords(item, data_label, used_once, keywords)
                        if keywords:
                            return keywords
                            # break
        raise raiseExceptions("data label is not found!")

    def compare_all_keywords_for_data_label(self, lists):
        """
        # lists: 所有数据的关键字的集合，如items字段对应的所有数据的关键字的集合
        # 功能：对比所有的关键字集合是不是一样
        """
        if lists.count(lists[0]) == len(lists):
            return True
        else:
            raise raiseExceptions("the keywords for data label is not the same!")

    def get_result_for_data_label(self, data_label, json_data, index=0):
        """
    # data_label: 数据的标签， 如items
    # json_data: 字典格式的json数据
    # index: 需要查找的数据的索引，默认值0代表查找第一个数据
    # 功能：返回指定的index的items里面的数据
        """
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

    def get_all_results_for_data_label(self, data_label, json_data):
        """
        # data_label: 数据的标签， 如items
        # json_data: 字典格式的json数据
        # 功能：返回items的所有数据
        """
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

    def get_max_pages(self, url, data_label, page_keyword, data=None, headers=None, default_per_page=10):
        """
        # url: 测试的url
        # data_label: 数据的标签， 如items
        # page_keyword: 页数的关键字，如pageNum
        # data: url请求时发送的数据
        # headers: url请求时发送的消息头
        # default_per_page: 每一页默认的数据数量
        # 获取最大的页数和数据的总量，可以单独调用这个函数测试json数据里面的页数和数据总量是不是正确
        """
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

    def per_page_test(self, times, url, data_label, page_keyword, per_page_keyword, max_page_number=None, total_number=None, data=None, headers=None, default_per_page=10):
        """
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
        """
        count = 0
        passed_times = 0
        if not max_page_number and not total_number:
            max_page_number, total_number = self.get_max_pages(url, data_label, page_keyword, data, headers, default_per_page)
        while count < times:
            page_number = random.choice(range(1, max_page_number))
            default_per_page = random.choice(range(1, total_number))
            if page_number*default_per_page < total_number:
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

    def check_mandatoryList(self, list_defined, list_result):
        """
        检查强制的参数在结果里面是否都存在
        :param list_defined: 强制的参数集合,格式可以是[parameter1, parameter2], 也可以为了定义方便写成"[parameter1, parameter2]"
        :param list_result: 实际结果里面的关键字集合，格式为[]或者[[], []]，可以通过get_data_label_keywords，并且传递all=True或者False的方式获取
        :return: True/False, 如果返回为False, 同时会打印出错的地方和值
        """
        if type(list_defined) == str or type(list_defined) == unicode:
            list_defined = eval(list_defined)
        if len(filter(lambda x: type(x) == list, list_result)) == len(list_result):
            if len(filter(lambda x: sorted(list(set(list_defined).intersection(set(x)))) == sorted(list_defined), list_result)) == len(list_result):
                return True
            else:
                differences = map(lambda x: list(set(list_defined).difference(set(x))), list_result)
                count = 0
                while count < len(differences):
                    if differences[count]:
                        print "the " + str(count) + " value is wrong!"
                        print "missed madatory paramters: " + str(differences[count])
                        print "defined madatory paramters: " + str(list_defined)
                    count += 1
                return False
        else:
            if sorted(list(set(list_defined).intersection(set(list_result)))) == sorted(list_defined):
                return True
            else:
                print "missed madatory paramters: " + str(list(set(list_defined).difference(set(list_result))))
                print "defined madatory paramters: " + str(list_defined)
                return False

    def check_list_unique(self, list_defined):
        """
        判断一个list的是否出现了重复的值
        :param list_defined: 需要传递一个list的参数进来,格式可以是[parameter1, parameter2], 也可以为了定义方便写成"[parameter1, parameter2]"
        :return: True/False，如果返回为False, 同时会打印出错的地方和值
        """
        if type(list_defined) == str or type(list_defined) == unicode:
            list_defined = eval(list_defined)
        if len(list(set(list_defined))) == len(list_defined):
            return True
        else:
            value = collections.Counter(list_defined)
            for key in value:
                if value[key] > 1:
                    print str(key) + " is repeated " + str(value[key]) + " times!"
            return False

    def check_value_type(self, value, type_defined):
        """
        RobotFramework专用
        传入值和期望的类型进行比对
        Args:
            value:
            type_defined: long, str, dict, list, int

        Returns: True/False，如果返回为False, 同时会打印出错的地方和值

        """
        if type(value) == eval(type_defined):
            return True
        else:
            print "the value is: " + str(value)
            print "excepted type is: " + str(type_defined)
            print "actual type is: " + str(type(value))
            return False

    def check_value_types(self, values, types_defined):
        """
         RobotFramework专用
        传入值和期望的类型进行比对
        :param values: 格式为{}或者[{},{}]
        :param types_defined: 格式为{parameter1: type1, parameter2: type2}, 为了方便在robotframework里面也可以定义为“{parameter1: type1, parameter2: type2}”做为字符串的形式传入
        :return: True/False, 如果返回为False, 同时会打印出错的地方和值
        """
        if type(types_defined) == str or type(types_defined) == unicode:
            types_defined = eval(types_defined)
        flag = False
        if type(values) == dict:
            if len(filter(lambda x: type(values[x]) == eval(types_defined[x]), types_defined)) == len(types_defined):
                flag = True
            else:
                count = 0
                while count < len(types_defined):
                    if eval(types_defined[types_defined.keys()[count]]) != type(values[types_defined.keys()[count]]):
                        print "number of parameter: " + str(count)
                        print "parameter is: " + str(types_defined.keys()[count])
                        print "defined type: " + str(eval(types_defined[types_defined.keys()[count]]))
                        print "actual type: " + str(type(values[types_defined.keys()[count]]))
                    else:
                        pass
                    count += 1
        elif type(values) == list:
            if len(filter(lambda x: type(x) == dict, values)) != len(values):
                print "the values structure is wrong, please use {} or [{}, {}] as the format the values!"
            else:
                flag_count = 0
                for value in values:
                    if len(filter(lambda x: type(value[x]) == eval(types_defined[x]), types_defined)) == len(types_defined):
                        flag_count += 1
                    else:
                        count = 0
                        while count < len(types_defined):
                            if eval(types_defined[types_defined.keys()[count]]) != type(value[types_defined.keys()[count]]):
                                print "number of parameter: " + str(count)
                                print "parameter is: " + str(types_defined.keys()[count])
                                print "defined type: " + str(eval(types_defined[types_defined.keys()[count]]))
                                print "actual type: " + str(type(value[types_defined.keys()[count]]))
                            else:
                                pass
                            count += 1
                if flag_count == len(values):
                    flag = True
        if flag:
            return True
        else:
            return False

    def random_str(self, randomlength=8):
        """

        :param randomlength: 默认生成8位随机字符串， 可以传入自己定义的位数
        :return: 指定位数的字符串
        """
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    def test(self):
        return 1, 2
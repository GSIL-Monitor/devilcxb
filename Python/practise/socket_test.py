# -*- coding: cp936 -*-
import urllib
import urllib2
import time
import sys
from collections import Counter
import random
import chardet


class Socket_test(object):
    def __init__(self, socket_url, params_need_to_get, params_from_result_defined, body, headers):
        self.socket_url = socket_url
        self.params_need_to_get = params_need_to_get
        self.params_from_result_defined = params_from_result_defined
        self.body = body
        self.headers = headers
        global null
        null = ""

    def nice_print(self, message, sign='*'):
        '''
            Printing nice banners
        '''
        print(''.join([' ', sign*len(message)]))
        print(''.join([' ', message]))
        print(''.join([' ', sign*len(message)]))

    def get_result(self, socket_url, params=None):
        if params is not None:
            params = urllib.urlencode(params)
        else:
            params = ""
        self.nice_print(socket_url + " is starting to test with parameters " + str(params))
        if "?" not in socket_url:
            socket_url = socket_url + "?"
        result = urllib2.urlopen(socket_url + params).read()
        return eval(result)

    def get_items_result(self,result):
        return self.get_final_result(result[self.body])

    def get_all_items_from_list(self, source_list, return_list):
        for i in source_list:
            if type(i) == list:
               self.get_all_items_from_list(i, return_list)
            else:
                return_list.append(i)
        return return_list

    def get_final_result(self,result):
        if type(result) == dict:
            if len(filter(lambda key:type(result[key]) == list, result.keys())) == len(result.values()):
                result = self.get_final_result(result.values())
        elif type(result) == list:
            result = self.get_all_items_from_list(result, [])
        return result

    def headers_test(self, result):
        #print filter(lambda x: x not in self.headers.keys(), filter(lambda x: x != self.body, result.keys()))
        #print filter(lambda x: x not in filter(lambda x: x != self.body, result.keys()), self.headers.keys())
        if len(filter(lambda x: x not in self.headers.keys(), filter(lambda x: x != self.body, result.keys()))) == 0 and len(filter(lambda x: x not in filter(lambda x: x != self.body, result.keys()), self.headers.keys())) == 0:
            for key in self.headers.keys():
                if type(result[key]) != int:
                    #print chardet.detect(result[key])['encoding']
                    result[key] = result[key].decode(chardet.detect(result[key])['encoding'])
            if filter(lambda x: result[x] in self.headers[x], self.headers.keys()) == self.headers.keys():
                self.nice_print("headers is tested passed!")
            else:
                self.nice_print("value of headers is out of range: " + str(map(lambda x: result[x], self.headers.keys())) + " " + str(self.headers.values()))
        else:
            self.nice_print("headers is mismatched:" + str(filter(lambda x: x != self.body, result.keys())) + " " + str(self.headers.keys()))

    def compare_params_keys_with_defined(self, params_from_result_defined, params_from_result_actual):
        if len(filter(lambda x: x not in params_from_result_defined, params_from_result_actual)) == 0 and len(filter(lambda x: x not in params_from_result_actual, params_from_result_defined)) == 0:
            return True
        else:
            self.nice_print("please refer to the parameters as below that defined is more than actual:")
            print filter(lambda x: x not in params_from_result_actual, params_from_result_defined)
            self.nice_print("please refer to the parameters as below that actual is more than defined:")
            print filter(lambda x: x not in params_from_result_defined, params_from_result_actual)
            return False

    def compare_params_keys_from_result(self, items_result, params_from_result_defined):
        #print items_result
        items_result_keys = map(lambda x: str(x.keys()),items_result)
        if len(Counter(items_result_keys)) == 1 or len(Counter(items_result_keys)) == 0:
            try:
                params_from_result_actual = eval(Counter(items_result_keys).items()[0][0])
            except IndexError:
                params_from_result_actual = []
            #print params_from_result_actual
            if self.compare_params_keys_with_defined(params_from_result_defined, params_from_result_actual):
                self.nice_print("compare keys between result and defined is passed!")
            else:
                self.nice_print("compare keys between result and defined is failed!")
                #sys.exit(1)
        else:          
            self.nice_print("there are different keys for all the items, please refer to the details as below:")
            for i in Counter(items_result_keys).items():
                print i
            #sys.exit(1)

    def get_max_pages(self, socket_url, page_number, default_per_page):
        if "?" not in socket_url:
            socket_url = socket_url + "?"
        #print default_per_page
        while len(self.get_items_result(self.get_result(socket_url + "&page=" + str(page_number)))) == default_per_page:
            #print page_number
            page_number = page_number + 1
        total_number = default_per_page*(page_number-1) + len(self.get_items_result(self.get_result(socket_url + "&page=" + str(page_number))))
        return page_number,total_number

    def per_page_test(self, socket_url, max_page_number, default_per_page, total_number, times):
        count = 0
        while count < times:
            page_number = random.choice(range(1,max_page_number))
            default_per_page = random.choice(range(1,total_number))
            if "?" not in socket_url:
                socket_url = socket_url + "?"
            if page_number*default_per_page < total_number:
                url = socket_url + "&page=" + str(page_number) + "&per_page=" + str(default_per_page)
                try:
                    if len(self.get_items_result(self.get_result(url))) == default_per_page:
                        self.nice_print("per_page is tested passed for the " + str(count) + " times!")
                        print "url is " + url 
                    else:
                        self.nice_print("per_page is tested failed for the " + str(count) + " times!")
                        print "url is " + url
                        sys.exit(1)
                    count += 1
                except KeyError:
                    info=sys.exc_info()
                    print info[0],":",info[1]
                    print "url is " + url            
        
    def main(self):
        self.nice_print(socket_url + " is starting to test!")
        for param_need_to_get_key in params_need_to_get.keys():
            if "page" in params_need_to_get.keys():
                if "per_page" in params_need_to_get.keys():
                    default_per_page = params_need_to_get["per_page"]
                else:
                    default_per_page = 10
                max_page_number, total_number = self.get_max_pages(socket_url,params_need_to_get["page"], default_per_page)
                self.nice_print("page is tested passed and total pages are: " + str(max_page_number))
                if "per_page" in params_need_to_get.keys():
                    self.per_page_test(socket_url, max_page_number, default_per_page, total_number, 10)
            for True_value in params_need_to_get[param_need_to_get_key]["True"]:
                print socket_url
                print {param_need_to_get_key:True_value}
                result = self.get_result(socket_url, {param_need_to_get_key:True_value})
                #print result
                self.headers_test(result)
                items_result = self.get_items_result(result)
                self.compare_params_keys_from_result(items_result, params_from_result_defined["True"])
            for False_value in params_need_to_get[param_need_to_get_key]["False"]:
                result = self.get_result(socket_url, {param_need_to_get_key:False_value})
                #print result
                self.headers_test(result)
                items_result = self.get_items_result(result)
                self.compare_params_keys_from_result(items_result, params_from_result_defined["False"])
        if len(params_need_to_get.keys()) == 0:
            result = self.get_result(socket_url)
            #print result
            self.headers_test(result)
            items_result = self.get_items_result(result)
            self.compare_params_keys_from_result(items_result, params_from_result_defined["True"])

if __name__ == "__main__":

    socket_url = "http://usercare-tcl-test.tclclouds.com/banner/save.json"
    headers = {"status": [1, 0], "msg": ["success", u"fail"]}
    body = "data"
    params_need_to_get = {"name":{"True":["testsave1"],"False":[]}, "imageUrl":{"True":["www.baidu.com"], "False": []}, "contentUrl":{"True":["www.baidu.com"], "False":[]}, #"per_page": 10
                           }
    params_from_result_defined = {"True": [], "False": []}
    socket_test = Socket_test(socket_url, params_need_to_get, params_from_result_defined, body, headers)
    socket_test.main()
    """
    socket_url = "http://usercare-test.tclclouds.com/api/user/getuserManuals.json"
    headers = {"code": [0, 500], "msg": [u"成功", u"服务器异常"]}
    body = "data"
    params_need_to_get = {"model":{"True":["7040A", "6045Y"],"False":["6039Y"]}, #"per_page": 10
                           }
    params_from_result_defined = {"True": ["fileUrl", "supportLanguage", "languageCode"], "False": []}
    socket_test = Socket_test(socket_url, params_need_to_get, params_from_result_defined, body, headers)
    socket_test.main()
    """
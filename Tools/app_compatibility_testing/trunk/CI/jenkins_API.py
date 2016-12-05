# -*- coding: utf-8 -*-
import jenkinsapi.jenkins as jenkins
from jenkinsapi.queue import QueueItem, Queue
from jenkinsapi.custom_exceptions import NoBuildData
import sys
import requests
import time
import re
import urllib2
import urllib
import cookielib
# sys.path.append(r"E:\SVN\Tools\app_compatibility_testing\trunk")
from buz.BaseClass import BaseClass



class handle_jenkins(BaseClass):
    def __init__(self, jenkins_server, Username, Password):
        self.jenkins_server = jenkins_server
        self.Username = Username
        self.Password = Password
        # global server
        try:
            self.server = jenkins.Jenkins(self.jenkins_server, username=self.Username, password=self.Password)
            self.logger.info("jenkins server is connected!")
        except requests.exceptions.ConnectionError:
            infos = sys.exc_info()
            self.logger.error(infos[0], ":", infos[1])
        except requests.exceptions.HTTPError:
            info = sys.exc_info()
            if "401 Client Error" in info[1]:
                try:
                    self.server = jenkins.Jenkins(self.jenkins_server, username=self.Username, password=self.Password)
                except requests.exceptions.HTTPError:
                    infos = sys.exc_info()
                    if "401 Client Error" in info[1]:
                        self.logger.error(infos[0], ":", infos[1], "failed again!!!!!!!!!!")
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
           "Content-Type": "application/x-www-form-urlencoded"
           }
        autherization_info = {"j_username": self.Username, "j_password": self.Password, "Submit": "登录", "from": ""}
        autherization_url = self.jenkins_server + "j_acegi_security_check"
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request(autherization_url, data=urllib.urlencode(autherization_info), headers=self.headers)
        self.opener.open(req).read()
        urllib2.install_opener(self.opener)

    def build_job(self, job_name, params, nodeName=None):
        """
        通过urllib2构建job
        :param job_name: job名称
        :param params: 构建参数
        :return: None
        """
        build_params = {}
        build_params["params"] = params
        if nodeName:
            build_params["nodeName"] = nodeName
        post_url = self.jenkins_server + "/job/" + job_name + "/buildWithParameters?delay=0sec"
        self.opener.open(post_url, urllib.urlencode(build_params)).read()

    def build_job_old(self, job_name, params, nodeName=None):
        # print self.params
        build_params = {}
        build_params["params"] = params
        if nodeName:
            build_params["nodeName"] = nodeName
        count = 1
        while count < 10:
            try:
                self.server.build_job(job_name, params=build_params)
                break
            except:
                count += 1

    def build_job_new(self, job_name, params):
        """
        通过urllib2构建job
        :param job_name: job名称
        :param params: 构建参数
        :return: None
        """
        post_url = self.jenkins_server + "/job/" + job_name + "/buildWithParameters?delay=0sec"
        self.opener.open(post_url, urllib.urlencode(params)).read()

    def cancel_job(self, job_name, taskid):
        flag = False
        query = Queue("%squeue" % self.jenkins_server, self.server)
        for i in query._get_queue_items_for_job(job_name):
            if eval(i.get_parameters()["params"])["task_id"] == taskid:
                query.delete_item(i)
                flag = True
                break
        return flag

    def get_running_objects(self, job_name):
        """
        获取正在运行的job的build对象
        :param job_name: job名称
        :return: 正在构建的build对象
        """
        running_list = []
        for i in range(self.server.jobs[job_name].get_last_completed_buildnumber() + 1,
                       self.server.jobs[job_name].get_last_buildnumber() + 1):
            running_list.append(self.server.jobs[job_name].get_build(i))
        return running_list

    def convert(self, value, job_name):
        # value = map(lambda x: dict(server_address=x[1][:-1], id=x[0][:-1], node_name=x[2][:-1]), value)
        if job_name == self.get_jenkins_info().get('compatibility_job_name'):
            value = map(lambda x: {x[2][:-1].split("_")[-1]: {"server_address": x[1][:-1], "id": x[0][:-1]}}, value)
            return value
        elif job_name == self.get_jenkins_info().get('safety_cancel_name'):
            try:
                device = re.findall("\[NodeParameterValue: nodeName=(.*?\])", value[0])[0][:-1].split("_")[-1]
            except:
                self.logger.error(str(value))
            return  map(lambda x: map(lambda x: {device: {"id": x[0][:-1], "server_address": x[1][:-1]}}, x), filter(lambda x: x, map(lambda x: re.findall("&amp;#039;id&amp;#039;: (.*?,).*?server_address&amp;#039;: &amp;#039(.*?&)", x), value)))


    def get_final_values(self, contents, compile_reg, job_name, running_values):
        if not filter(lambda x: job_name.replace("_", "<wbr>_") in x and "params=" in x, contents):
            values = []
        else:
            values = map(lambda x: self.convert(re.findall(compile_reg, x), job_name), filter(lambda x: job_name.replace("_", "<wbr>_") in x and "params=" in x and re.findall(compile_reg, x), contents))
        if not values:
            if not running_values:
                return {}
            else:
                values = running_values
        else:
            if not running_values:
                values = reduce(lambda x, y: x + y, values)
            else:
                values = reduce(lambda x, y: x + y, values) + running_values
        if job_name == self.get_jenkins_info().get('safety_cancel_name'):
            values = map(lambda x: {x[0].keys()[0]: {"server_address": x[0].values()[0]["server_address"], "id": map(lambda x: x.values()[0]["id"], x)}}, values)
        devices = list(set(map(lambda x: x.keys()[0], values)))
        final_result = {}
        for device in devices:
            if job_name == self.get_jenkins_info().get('compatibility_job_name'):
                final_result[device] = map(lambda x: x[device], filter(lambda x: x.keys()[0] == device, values))
            elif job_name == self.get_jenkins_info().get('safety_cancel_name'):
                final_result[device] = map(lambda x: x.values()[0], filter(lambda x: x.keys()[0] == device, values))
        return final_result

    def get_running_taskids_from_device(self, job_name, running_urls):
        if job_name == self.get_jenkins_info().get('compatibility_job_name'):
            return map(lambda x: {x["nodeName"][:-1].split("_")[-1]: {'server_address': x["server_address"][:-1], "id": x["appinfo_id"][:-1]}}, map(lambda x: re.match(".*'nodeName': u'(?P<nodeName>.*?').*?'appinfo_id': (?P<appinfo_id>.*?,).*?'server_address': ?'(?P<server_address>htt[p|ps].*?')", filter(lambda x: re.match(".*'nodeName': u'(?P<nodeName>.*?').*?'appinfo_id': (?P<appinfo_id>.*?,).*?'server_address': ?'(?P<server_address>htt[p|ps].*?')", x), urllib2.urlopen(x).readlines())[0]).groupdict(), running_urls))
        elif job_name == self.get_jenkins_info().get('safety_cancel_name'):
            running_values = []
            for running_url in running_urls:
                contents = urllib2.urlopen(running_url).readlines()
                device = re.findall('name="label" value="(.*?")', filter(lambda x: re.search('name="label" value="(.*?")', x), contents)[0])[0][:-1].split("_")[-1]
                try:
                    running_values.append(map(lambda x: {device: {"server_address": x[0][:-1].strip(), "id": x[1][:-1]}}, re.findall("'server_address.*?'(htt[p|ps].*?').*?'id.*? (.*?,)", filter(lambda x: re.search("'server_address.*?'(htt[p|ps].*?').*?'id.*? (.*?,)", x), contents)[0])))
                except IndexError:
                    try:
                        running_values.append(map(lambda x: {device: {"server_address": x[1][:-1].strip(), "id": x[0][:-1]}}, re.findall("'id.*? (.*?,).*?'server_address.*? '(htt[p|ps].*?')", filter(lambda x: re.search("'id.*? (.*?,).*?'server_address.*? '(htt[p|ps].*?')", x), contents)[0])))
                    except:
                        self.logger.error(str(str(contents)))
            return running_values

    def get_query_taskids_from_device(self, job_name):
        contents = urllib2.urlopen(self.jenkins_server).readlines()
        running_herfs = map(lambda x: re.findall('href="/jenkins/(job/' + job_name + '/\d+/)console', x)[0], filter(lambda x: re.search('href="/jenkins(/job/' + job_name + '/\d+/console)', x), contents))
        running_values = []
        if running_herfs:
            running_urls = map(lambda x: self.jenkins_server + x + "parameters/", running_herfs)
            running_values = self.get_running_taskids_from_device(job_name, running_urls)
        if job_name == self.get_jenkins_info().get('compatibility_job_name'):
            compile_reg = ".*?params=.*?appinfo_id.*?: (.*?,).*?server_address&amp;#039;: &amp;#039;(.*?&).*?\[NodeParameterValue: nodeName=(.*?\]).*?" + job_name.replace("_", "<wbr>_")
        elif job_name == self.get_jenkins_info().get('safety_cancel_name'):
            compile_reg = ".*?params=.*?securityTest</a>"
        return self.get_final_values(contents, compile_reg, job_name, running_values)

    def get_query_taskids_from_device_bk(self, job_name):
        """
        获取相应job在每一个节点上面排队的taskid
        :param job_name: job名称
        :return: device ID和对应的task ID
        """
        query_items = {}
        count = 1
        while count < 10:
            try:
                self.server.jobs[job_name].get_last_build()._data
                break
            except:
                count += 1
        query = Queue(self.jenkins_server + "queue", self.server)
        try:
            for i in (query.get_queue_items_for_job(job_name) + self.get_running_objects(job_name)):
                i = i._data
                # print i
                if "actions" in i.keys():
                    for item in i["actions"]:
                        if "parameters" in item.keys():
                            for value_item in item["parameters"]:
                                if "name" in value_item and value_item["name"] == "params":
                                    value = eval(value_item["value"])
                                if job_name == self.get_jenkins_info().get('safety_cancel_name'):
                                    if "name" in value_item and value_item["name"] == "nodeName":
                                        device_ID = value_item["value"]
                            break
                    if job_name == self.get_jenkins_info().get('compatibility_job_name'):
                        device_ID = value["nodeName"].split("_")[-1]
                        appinfo_ID = value["appinfo_id"]
                        server_address = value["server_address"]
                    elif job_name == self.get_jenkins_info().get('safety_cancel_name'):
                        appinfo_ID = []
                        first_flag = False
                        for item in value["scanInfo"]:
                            appinfo_ID.append(item["id"])
                            if not first_flag:
                                server_address = item["server_address"]
                                first_flag = True
                    if device_ID not in query_items.keys():
                        query_items[device_ID] = [{"id": appinfo_ID, "server_address": server_address}]
                    else:
                        query_items[device_ID].append({"id": appinfo_ID, "server_address": server_address})
        except NoBuildData:
            query_items = {}
        return query_items


if __name__ == "__main__":
    jenkins_server = 'http://10.115.101.230:8080/jenkins/'
    Username = "xiaobo.chi"
    Password = "DEVIL_cxb2"
    job_name = "app_compatibility_testing"
    taskid = "0bafed11-346c-11e6-87d8-ecb1d75350d2"
    nodeName = ""
    params = "{params:{'deviceid': '134', 'apkPath': '\\\\10.115.101.231\\AppstoreData\\upload_apk\\tclmarket-V5.0.0-2015-12-10-release_test.apk ', 'packageName': 'com.tclmarket', 'appinfo_id': 73, 'mainActivity': 'com.tclmarket.sz.activity.WelcomeActivity', 'result': 0, 'versionName': '5.0.0', 'versioncode': '5.0.0', 'deviceno': 'a972d6b6', 'uid': '1'}, 'nodeName': 'CD_VAL55_9902_idol3_cn_5.0.2_16f6ce25'}"
    handle_jenkins = handle_jenkins(jenkins_server, Username, Password)
    # handle_jenkins.build_job(job_name, params, nodeName="test")
    print handle_jenkins.opener.open("http://10.115.101.230:8080/jenkins/view/VAL_Test/job/securityTest/876/parameters/").readlines()
    #  print handle_jenkins.get_query_taskids_from_device(job_name)
    # values = handle_jenkins.get_query_taskids_from_device("app_compatibility_testing")
    # print handle_jenkins.server.get_job("app_compatibility_testing").get_last_build()._data
    # query = Queue(handle_jenkins.jenkins_server + "queue", handle_jenkins.server)
    # print query.get_queue_items_for_job("test")

    # values = handle_jenkins.get_query_taskids_from_device("app_compatibility_testing")
    # print values
    # for value in values.keys():
    #     print value
    #     print values[value]

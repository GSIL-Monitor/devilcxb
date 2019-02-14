# -*- coding: utf-8 -*-
import jenkinsapi.jenkins as jenkins
from jenkinsapi.queue import QueueItem,Queue
import sys
import requests
import logging
import urllib2
import urllib
import cookielib
import re
logging.basicConfig(level=logging.INFO)


class HandleJenkins(object):
    def __init__(self, jenkins_server, username, password):
        """
        初始化Jenkins客户端的连接
        :param jenkins_server: Jenkins server的地址， 如：http://10.115.101.230:8080/jenkins/
        :param username: 认证的用户名
        :param password: 认证的密码
        :return: None
        """
        self.jenkins_server = jenkins_server
        self.username = username
        self.password = password
        try:
            self.server = jenkins.Jenkins(self.jenkins_server, username=self.username, password=self.password)
            logging.info("jenkins server is connected!")
        except requests.exceptions.ConnectionError:
            info = sys.exc_info()
            logging.error("jenkins is connected failed!")
            sys.exit(1)
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
           "Content-Type": "application/x-www-form-urlencoded"
           }
        autherization_info = {"j_username": self.username, "j_password": self.password, "Submit": "登录", "from": ""}
        autherization_url = self.jenkins_server + "j_acegi_security_check"
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request(autherization_url, data=urllib.urlencode(autherization_info), headers=self.headers)
        self.opener.open(req).read()
        urllib2.install_opener(self.opener)

    def get_all_nodes(self):
        """
        获取所有node的名称
        :return: 返回所有node的名称
        """
        return self.server.get_nodes().keys()

    def node_existed(self, node_name):
        """
        判断salve是否存在
        :param node_name: slave名称
        :return: True or False
        """
        try:
            self.opener.open(self.jenkins_server + "/computer/" + node_name).read()
            return True
        except urllib2.HTTPError:
            return False
        # return self.server.has_node(node_name)

    def create_node(self, node_name, based_node_name):
        """
        因为jenkinsapi库所包含的创建slave的方式比较单一，所以采用url请求post的方式创建slave,
        :param node_name: 需要创建的slave名称
        :param based_node_name: 需要复制的slave名称
        :return: True或者脚本执行中断
        """

        create_node_url = self.jenkins_server + "computer/createItem"
        data = {
            "name": node_name,
            "mode": "copy",
            "from": based_node_name,
            "Submit": "OK"
        }
        req = urllib2.Request(create_node_url, self.headers)
        self.opener.open(req, urllib.urlencode(data)).read()
        if self.server.has_node(node_name):
            logging.info(node_name + " is created successfully!")
            return True
        else:
            logging.debug(node_name + " is created failed!")
            sys.exit(1)

    def is_node_online(self, node_name):
        """
        判断node是否online
        :param node_name: slave的名称
        :return: True or False
        """
        try:
            result = self.opener.open(self.jenkins_server + "/computer/" + node_name).read()
            if "Mark this node temporarily offline" in result and "Launch agent from browser" not in result:
                return True
            return False
        except urllib2.HTTPError:
            return False
        # return self.server.nodes[node_name].is_online()

    def is_node_temporarily_offline(self, node_name):
        """
        判断node是否temporarily offline
        :param node_name: slave的名称
        :return: True or False
        """
        return self.server.nodes[node_name].is_temporarily_offline()

    def online_node(self, node_name):
        """
        上线slave
        :param node_name: slave的名称
        :return: True或者中断脚本
        """
        if self.is_node_online(node_name):
            logging.info(node_name + " is online!")
            return True
        else:
            # 2016/10/28 use urllib2 instead
            # self.server.nodes[node_name].set_online()
            self.opener.open(self.jenkins_server + "/computer/" + node_name + "/toggleOffline", data=urllib.urlencode({"Submit": "Bring+this+node+back+online"})).read()
            if self.is_node_online(node_name):
                logging.info(node_name + " is online!")
                return True
            else:
                logging.error(node_name + " is online failed!")
                sys.exit(1)

    def offline_node(self, node_name, message="requested from jenkinsapi"):
        """
        下线slave
        :param node_name: slave的名称
        :return: True或者中断脚本
        """
        if self.server.nodes[node_name].is_temporarily_offline():
            logging.info(node_name + " is offline!")
            return True
        else:
            self.server.nodes[node_name].set_offline(message=message)
            if self.server.nodes[node_name].is_temporarily_offline():
                logging.info(node_name + " is offline!")
                return True
            else:
                logging.error(node_name + " is offline failed!")
                sys.exit(1)

    def change_agent_port(self, port):
        manager_url = self.jenkins_server + "configureSecurity/configure"
        logging.debug("需要优化!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        json_data = {"useSecurity": {"slaveAgentPort": {"type": "fixed", "value": port}, "disableRememberMe": False, "realm": {"value": "1", "stapler-class": "hudson.security.LDAPSecurityRealm", "server": "ldap://172.26.32.57:3268", "rootDN": "DC=cd,DC=ta-mp,DC=com", "inhibitInferRootDN": False, "userSearchBase": "", "userSearch": "sAMAccountName={0}", "userIdStrategyClass": "jenkins.model.IdStrategy$CaseInsensitive", "groupIdStrategyClass": "jenkins.model.IdStrategy$CaseInsensitive", "groupSearchBase": "", "groupSearchFilter": "", "groupMembershipStrategy": {"value": "1", "filter": "", "stapler-class": "jenkins.security.plugins.ldap.FromGroupSearchLDAPGroupMembershipStrategy", "kind": "jenkins.security.plugins.ldap.FromGroupSearchLDAPGroupMembershipStrategy"}, "managerDN": "CN=gcquery,CN=Users,DC=cd,DC=ta-mp,DC=com", "managerPasswordSecret": "MU8LGJ3QEKPdJ4Z/uSO0mGgAUNaE+CPGKT6a/AnRb4o=", "displayNameAttributeName": "displayname", "mailAddressAttributeName": "mail", "disableMailAddressResolver": True}, "authorization": {"value": "2", "stapler-class": "hudson.security.GlobalMatrixAuthorizationStrategy", "data": {"TCloud": {"hudson.model.Hudson.Administer": False, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": False, "hudson.model.Hudson.UploadPlugins": False, "hudson.model.Hudson.ConfigureUpdateCenter": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": False, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": False, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": False, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": False, "hudson.model.Computer.Delete": False, "hudson.model.Computer.Create": False, "hudson.model.Computer.Disconnect": False, "hudson.model.Computer.Connect": False, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": False, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": False, "hudson.model.Run.Delete": False, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "UserRole": {"hudson.model.Hudson.Administer": False, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": False, "hudson.model.Hudson.UploadPlugins": False, "hudson.model.Hudson.ConfigureUpdateCenter": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": False, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": False, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": False, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": False, "hudson.model.Computer.Delete": False, "hudson.model.Computer.Create": False, "hudson.model.Computer.Disconnect": False, "hudson.model.Computer.Connect": False, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": False, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": False, "hudson.model.Run.Delete": False, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "jenkins": {"hudson.model.Hudson.Administer": True, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": True, "hudson.model.Hudson.UploadPlugins": True, "hudson.model.Hudson.ConfigureUpdateCenter": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": True, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": True, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": True, "hudson.model.Computer.Delete": True, "hudson.model.Computer.Create": True, "hudson.model.Computer.Disconnect": True, "hudson.model.Computer.Connect": True, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": True, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": True, "hudson.model.Run.Delete": True, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "jenkins.cdval": {"hudson.model.Hudson.Administer": True, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": True, "hudson.model.Hudson.UploadPlugins": True, "hudson.model.Hudson.ConfigureUpdateCenter": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": True, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": True, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": True, "hudson.model.Computer.Delete": True, "hudson.model.Computer.Create": True, "hudson.model.Computer.Disconnect": True, "hudson.model.Computer.Connect": True, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": True, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": True, "hudson.model.Run.Delete": True, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "xiaobo.chi": {"hudson.model.Hudson.Administer": True, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": True, "hudson.model.Hudson.UploadPlugins": True, "hudson.model.Hudson.ConfigureUpdateCenter": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": True, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": True, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": True, "hudson.model.Computer.Delete": True, "hudson.model.Computer.Create": True, "hudson.model.Computer.Disconnect": True, "hudson.model.Computer.Connect": True, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": True, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": True, "hudson.model.Run.Delete": True, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "xinjiu.qiao": {"hudson.model.Hudson.Administer": True, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": True, "hudson.model.Hudson.UploadPlugins": True, "hudson.model.Hudson.ConfigureUpdateCenter": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": True, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": True, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": True, "hudson.model.Computer.Delete": True, "hudson.model.Computer.Create": True, "hudson.model.Computer.Disconnect": True, "hudson.model.Computer.Connect": True, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": True, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": True, "hudson.model.Run.Delete": True, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}, "anonymous": {"hudson.model.Hudson.Administer": False, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": False, "hudson.model.Hudson.UploadPlugins": False, "hudson.model.Hudson.ConfigureUpdateCenter": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": False, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": False, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": False, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": False, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": False, "hudson.model.Computer.Configure": False, "hudson.model.Computer.Delete": False, "hudson.model.Computer.Create": False, "hudson.model.Computer.Disconnect": False, "hudson.model.Computer.Connect": True, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": False, "hudson.model.Item.Delete": False, "hudson.model.Item.Configure": False, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": False, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": False, "hudson.model.Item.Cancel": False, "hudson.model.Run.Delete": False, "hudson.model.Run.Update": False, "hudson.model.View.Create": False, "hudson.model.View.Delete": False, "hudson.model.View.Configure": False, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": False},"ling.xie": {"hudson.model.Hudson.Administer": False, "hudson.model.Hudson.Read": True, "hudson.model.Hudson.RunScripts": False, "hudson.model.Hudson.UploadPlugins": False, "hudson.model.Hudson.ConfigureUpdateCenter": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Create": False, "com.cloudbees.plugins.credentials.CredentialsProvider.Update": False, "com.cloudbees.plugins.credentials.CredentialsProvider.View": True, "com.cloudbees.plugins.credentials.CredentialsProvider.Delete": False, "com.cloudbees.plugins.credentials.CredentialsProvider.ManageDomains": False, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.ManualTrigger": True, "com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl.Retrigger": True, "hudson.model.Computer.Configure": False, "hudson.model.Computer.Delete": False, "hudson.model.Computer.Create": False, "hudson.model.Computer.Disconnect": False, "hudson.model.Computer.Connect": False, "hudson.model.Computer.Build": True, "hudson.model.Item.Create": True, "hudson.model.Item.Delete": False, "hudson.model.Item.Configure": True, "hudson.model.Item.Read": True, "hudson.model.Item.Discover": True, "hudson.model.Item.Build": True, "hudson.model.Item.Workspace": True, "hudson.model.Item.Cancel": False, "hudson.model.Run.Delete": False, "hudson.model.Run.Update": True, "hudson.model.View.Create": True, "hudson.model.View.Delete": True, "hudson.model.View.Configure": True, "hudson.model.View.Read": True, "hudson.scm.SCM.Tag": True}}, "": ""}}, "": "1", "markupFormatter": {"stapler-class": "org.jenkins_ci.plugins.pegdown_formatter.PegDownFormatter", "extensions": {"name": "SUPPRESS_ALL_HTML", "flag": "196608", "selected": True}, "advancedExtensions": [{"name": "ABBREVIATIONS", "flag": "4", "selected": True}, {"name": "AUTOLINKS", "flag": "16", "selected": True}, {"name": "DEFINITIONS", "flag": "64", "selected": True}, {"name": "FENCED_CODE_BLOCKS", "flag": "128", "selected": True}, {"name": "HARDWRAPS", "flag": "8", "selected": True}, {"name": "NO_FOLLOW_LINKS", "flag": "262144", "selected": True}, {"name": "SMARTYPANTS", "flag": "3", "selected": True}, {"name": "TABLES", "flag": "32", "selected": True}]}, "hudson-security-csrf-GlobalCrumbIssuerConfiguration": {}, "jenkins-security-s2m-MasterKillSwitchConfiguration": {}, "core:apply": ""}
        data = {
            "json": json_data,
            "Submit": "保存"
            }
        req = urllib2.Request(manager_url, headers=self.headers)
        self.opener.open(req, urllib.urlencode(data)).read()

    def cancel_all_build(self, job_name):
        """
        取消一个job上面所有排队的构建
        :param job_name: job名称
        :return: True/False
        """
        query = Queue(self.jenkins_server + "queue", self.server)
        for i in query._get_queue_items_for_job(job_name):
            query.delete_item(i)
        if len(query._get_queue_items_for_job(job_name)) == 0:
            return True
        else:
            return False

    def temporarily_offline_node_noConnection(self, nodeName, message = ""):
        """
        第一次创建slave或者salve在对应的PC上面并没有建立连接的时候，尝试temporiarily offline node.
        采用urllib的方式是因为jenkinsAPI对于这种状态的node操作temporarily offline会不成功
        :param nodeName: node名称
        :return: True/False
        """
        if not self.server.nodes[nodeName].is_temporarily_offline():
            url = self.jenkins_server + "computer/" + nodeName + "/toggleOffline"
            data = {
                "offlineMessage": message,
                "Submit": "Mark+this+node+temporarily+offline"
            }
            self.opener.open(url, data=urllib.urlencode(data)).read()
        logging.info(nodeName + " is tempririly offline!")
        return self.server.nodes[nodeName].is_temporarily_offline()

    def remove_node(self, nodeName):
        """
        删除Slave
        :param nodeName: Slave名称
        :return: True/False
        """
        if self.node_existed(nodeName):
            self.server.delete_node(nodeName)
        if not self.node_existed(nodeName):
            logging.info(nodeName + " is removed or not existed!")
            return True
        else:
            logging.error(nodeName + " is removed failed!")
            return False

    def has_query_items(self, nodeName):
        """
        判断Slave上面是否有排队的项目
        :param nodeName: Slave名称
        :return: True/False
        """
        query = Queue(self.jenkins_server + "queue", self.server)
        if nodeName in str(query._data):
            logging.info(nodeName + " has query items!")
            return True
        else:
            logging.info(nodeName + " does not have query items!")
            return False

    def query_items(self, nodeName):
        """
        判断Slave上面排队的项目
        :param nodeName: Slave名称
        :return: 排队的项目
        """
        data = []
        query = Queue(self.jenkins_server + "queue", self.server)
        return query._data["items"]

    def is_node_idle(self, nodeName):
        """
        判断node是不是正在跑任务
        :param nodeName: 节点名称
        :return: True/False
        """
        return self.server.nodes[nodeName].is_idle()

    def build_job(self, job_name, params=None, files=None):
        """
        构建Jenkins job
        :param job_name: job的名称
        :param params: 参数
        :param params: 文件参数特有格式为：{'<file_para_name>': open("path_of_file", "r")}
        :return: None
        """
        self.server.get_job(jobname=job_name).invoke(build_params=params, files=files)

    def build_job_new(self, job_name, params):
        """
        通过urllib2构建job
        :param job_name: job名称
        :param params: 构建参数
        :return: None
        """
        post_url = self.jenkins_server + "/job/" + job_name + "/buildWithParameters?delay=0sec"
        self.opener.open(post_url, urllib.urlencode(params)).read()

    def rebuild_jobs(self, job_name, start_number, end_number):
        """
        rebuild job
        :param job_name: job名称
        :param start_number: 开始的build number
        :param end_number: 结束的build number
        :return: None
        """
        for i in range(start_number, end_number + 1):
            params = {}
            for item in self.server.jobs[job_name].get_build(i).get_actions().get("parameters"):
                params[item["name"]] = item["value"]
            logging.info(job_name + " will be built with " + str(params))
            self.build_job(job_name, params)

    def get_build_number(self, job_name, conditions, start_number, end_number):
        """
        获取特定的构建号
        :param job_name: job名称
        :param conditions: 查询的条件，一般是用构建时用到的参数值或者参数值的部分做查询条件
        :param start_number: 开始的build number
        :param end_number: 结束的build number
        :return: 构建号/None
        """
        for i in range(start_number, end_number + 1):
            for item in self.server.jobs[job_name].get_build(i).get_actions().get("parameters"):
                if conditions in item["value"]:
                    logging.info("build number is " + str(i))
                    return i

    def cancel_jobs(self, job_name, conditions):
        query = Queue(self.jenkins_server + "queue", self.server)
        # self.server.jobs[job_name].delete_from_queue() #  method 2
        for i in query.get_queue_items_for_job(job_name):
            if conditions in str(i._data):
                query.delete_item(i)
                logging.info( str(i) + " is deleted!")

    def get_job_configurations(self, job):
        """
        获取job的XML配置
        :param job_name: job名称
        :return: job的XML配置
        """
        return self.server.get_job(job).get_config()

    def create_job(self, job_name, xml):
        """
        创建Job
        :param job_name: job名称
        :param xml: xml配置
        :return: None
        """
        self.server.create_job(job_name, xml)
        logging.info(job_name + " is created!")

    def get_descripotion_of_parameter(self, job_name, parameter_reg):
        """
        返回参数的描述
        :param job_name: job名称
        :param parameter_reg: 参数的正则表达式
        :return: 参数的描述
        """
        return filter(lambda x: re.match(parameter_reg, x["name"]), self.server.jobs[job_name]._data["actions"][0]["parameterDefinitions"])[0]["description"]

    def remove_job(self, job_name):
        """
        删除job
        :param job_name: job名称
        :return: 参数的描述
        """
        self.server.delete_job(job_name)

    def create_node_with_label(self):
        self.server.create_node()

if __name__ == "__main__":
    HandleJenkins = HandleJenkins("http://10.115.101.230:8080/jenkins/", "jenkins.cdval", "I8IBz0U2TC")
    job_name = "app_compatibility_testing_test"
    params = {"params": "{'appName':+u'WiFi\u4fe1\u53f7\u589e\u5f3a\u5668',+'apkPath':+u'\\\\MIE-YANGWEI0-D2\\AppstoreData\\upload_apk\\20161028143437\\20161028143437\\com.syezon.wifi_3.1.2_5610.apk',+'serial_no':+u'9979205e-9cd8-11e6-99f1-ecb1d75350d2',+'result':+1,+'apk_local_Path':+u'\\\\MIE-YANGWEI0-D2\\AppstoreData\\upload_apk\\20161028143437\\20161028143437\\com.syezon.wifi_3.1.2_5610.apk',+'versioncode':+u'3.1.2',+'id':+556L,+'nodeName':+u'CD_VAL55_10114_idol347_5.0.2_a972d6b6',+'appinfo_id':+556L,+'task_id':+u'998a8580-9cd8-11e6-932a-ecb1d75350d2',+'packageName':+u'com.syezon.wifi',+'mainActivity':+u'com.syezon.wifi.LogoActivity',+'deviceid':+150L,+'run_performance':+0,+'deviceno':+u'a972d6b6',+'server_address':+'https://10.115.101.32:5001'}", "nodeName": "CD_VAL55_10072_HERO2_4.4.2_HUWGEALR9P4HMBHY1"}
    projects = {}
    for i in range(948, 1064):
        try:
            build_id = HandleJenkins.server.jobs["Monkey"].get_build(i)
            if build_id.is_good():
                upstream_job_name = build_id.get_upstream_job_name()
                project_name = upstream_job_name[:-(len(upstream_job_name.split("_")[-1]) + 1)]
                if project_name not in projects.keys():
                   projects[project_name] = 1
                else:
                   projects[project_name] = projects[project_name] + 1
        except:
            HandleJenkins.server = jenkins.Jenkins("http://10.115.101.230:8080/jenkins/", "jenkins.cdval", "I8IBz0U2TC")
            build_id = HandleJenkins.server.jobs["Monkey"].get_build(i)
            if build_id.is_good():
                upstream_job_name = build_id.get_upstream_job_name()
                project_name = upstream_job_name[:-len(upstream_job_name.split("_")[-1]) + 1]
                if project_name not in projects.keys():
                   projects[project_name] = 1
                else:
                   projects[project_name] = projects[project_name] + 1
    for key in projects.keys():
        print key, projects[key]

    # HandleJenkins.build_job_new(job_name, params)
    # HandleJenkins.online_node("CD_VAL97_10104_x1_plus_6.0.0_6DCE5HVW8PNFPNQS")
    # print HandleJenkins.is_node_online("CD_VAL55_10058_POP4-10_4G_6.0.1_36c4ee")
    # HandleJenkins.create_node("teeeeeeeeeeeeee", "CD_VAL55")
    # print HandleJenkins.cancel_all_build("app_compatibility_testing")
    # HandleJenkins.rebuild_jobs("app_compatibility_testing", 3729, 3774)
    # print HandleJenkins.get_build_number("app_compatibility_testing", "com.mq.lepetitnicolas", 4300, 4398)
    # HandleJenkins.cancel_jobs("app_compatibility_testing_test", "CD_VAL55_10018_POP4-10_4G_6.0.1_36c4ee")
    # HandleJenkins.cancel_jobs("app_compatibility_testing_test", "CD_VAL55_10018_POP4-10_4G_6.0.1_36c4ee")
    # HandleJenkins.cancel_jobs("app_compatibility_testing", "CD_VAL55_10058_POP4-10_4G_6.0.1_36c4ee")
    # print HandleJenkins.get_all_nodes()
    # print HandleJenkins.is_node_online("CD_VAL55_10055_HERO2_4.4.2_NJFUYHONJZ8TRKSO")
    """
    try:
        HandleJenkins.online_node("CD_VAL77_test")
    except Exception as e:
        if e.message == "Node is offline and not marked as temporarilyOffline, check client connection: offline = True, temporarilyOffline = False":
            print "OK"
    """
    # HandleJenkins.offline_node("CD_VAL97")
    # HandleJenkins.online_node("CD_VAL97")
    # HandleJenkins.remove_job("Examination_\xe2\x95\xa0\xd0\xb8\xd0\xbe\xd0\x9a\xd0\xbe\xd0\xbb")





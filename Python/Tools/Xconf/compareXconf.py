#!_*_ coding:utf-8 _*_
# Auther: Chi Xiaobo
# 2018.04.24: first draft
import urllib
import urllib2
import cookielib
import time
import ConfigParser, os, re, sys
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

global null, false, true
null = None
false = False
true = True


class GetXconf(object):
    def __init__(self, environment_name, project="zhenliang"):
        self.environment_name = environment_name
        if self.environment_name == "product":
            self.environment_type_code = "3"
        elif self.environment_name == "develop":
            self.environment_type_code = "1"
        else:
            self.environment_type_code = "2"
        config = ConfigParser.ConfigParser()
        config_file = os.path.join(os.path.dirname(__file__), '%s%sconfig.ini' % (project, os.sep))
        if os.path.isfile(config_file):
            logging.info("config file: %s" % (config_file))
        else:
            logging.error("config file is not existed: %s" % (config_file))
        config.read(config_file)
        # 获取xconf登录时用到的URL里面的host
        self.hosts = {environment_name: config.get(environment_name, "xconf_host")}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 获取xconf的用户名和密码
        self.auth_data = {"email": config.get(environment_name, "xconf_username"),
                          "password": config.get(environment_name, "xconf_password")}
        # TODO： 目前存在生产和测试环境不一致的服务名称，这里需要做一个映射，此处需要同步优化。
        self.product_test_services_map = {
            "loan-app-common": "loan-common",
            "loan-app-user": "loan-user",
            "loan-app-input": "loan-input",
            "loan-app-gateway-keeper": "gateway-keeper",
            "public-third": "profit-card-third",
            "profit-card-mall-app": "profid-card-mall-app"
        }
        # 此处可以设置需要忽略的服务名称
        self.ignore_services = ["loan-audit"]
        # 保存cookie到运行环境。
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        self.token = self.get_token()

    def get_token(self):
        """
        获取token
        :return:
        """
        login_url = "http://%s/login" % (self.hosts[self.environment_name])
        req = urllib2.Request(login_url, headers=self.headers)
        # print login_url
        # print self.auth_data
        # print self.headers
        token = eval(urllib2.urlopen(req, data=urllib.urlencode(self.auth_data)).read())["msg"]
        if token:
            logging.info("token: %s" % (token))
            return token
        else:
            logging.error("token is failed to get!")
            sys.exit("token is failed to get!")

    def add_token(self):
        """
        在header里面加入token
        :return:
        """
        self.headers["token"] = self.token

    def get_appid(self, app_name, cmp_name="zhenliang"):
        req_url = "http://%s/app/list?cmyName=&appName=" % (self.hosts[self.environment_name])
        req = urllib2.Request(req_url, headers=self.headers)
        datas = eval(self.opener.open(req).read())["data"]
        logging.info("appid information: %s" % (str(datas)))
        for data in datas:
            if data["cmp_name"] == cmp_name and data["app_name"] == app_name:
                return data["app_id"]

    def sync_zk(self, app_name, cmp_name, service_name):
        """
        目前直接更改数据库，不会马上生效，需要做一次同步操作。
        :param app_name: 项目名称
        :param cmp_name: 公司名称
        :param service_name: 服务名称
        :return:
        """
        self.add_token()
        req_url = "http://%s/cnf/refresh?appId=%s&kvType=2&serviceName=%s" % (
            self.hosts[self.environment_name], self.get_appid(app_name=app_name, cmp_name=cmp_name), service_name)
        logging.info(req_url)
        req = urllib2.Request(req_url, headers=self.headers)
        res = eval(self.opener.open(req).read())
        datas = res["data"]
        logging.info("sync dat to zk: %s" % (str(datas)))
        if res["msg"] == "Success" and type(datas) == list and len(datas) > 0:
            return True

    def get_services(self, appid):
        """
        根据appid获取service集合
        :param appid: appid
        :return: service集合
        """
        req_data = {
            "appId": appid,
            "type": self.environment_type_code
        }
        # print req_data
        req_url = "http://%s/cnf/serviceList" % (self.hosts[self.environment_name])
        req = urllib2.Request(req_url, headers=self.headers)
        if self.environment_name != "product":
            services = map(lambda x: x["server_name"],
                           eval(self.opener.open(req, data=urllib.urlencode(
                               req_data)).read())["data"])
        else:
            services = map(lambda x: x["server_name"].split("#")[-1],
                           # 生产环境目前针对服务名称，前面会加上smallloan#loan-debit-service这样的前缀，此处强行去掉#前面的东西
                           eval(self.opener.open(req, data=urllib.urlencode(
                               req_data)).read())["data"])
            count = 0
            product_test_services_map_keys = self.product_test_services_map.keys()
            while count < len(services):
                if services[count] in product_test_services_map_keys:
                    services[count] = self.product_test_services_map[services[count]]
                count += 1
        # print services
        services = filter(lambda x: x not in self.ignore_services, services)
        return services

    def get_xconf(self, apppid):
        """
        当前未使用，此采用urllib2返回json的方式，组合配置数据
        :param apppid: appid
        :return: 返回json格式的xconf配置数据
        """
        req_data = {
            "appId": apppid,
            "key": "",
            "limit": 1,
            "offset": 0,
            "serviceName": "",
            "type": self.environment_type_code
        }
        req_url = "http://%s/cnf/list" % (self.hosts[self.environment_name])
        req = urllib2.Request(req_url, headers=self.headers)
        return_data = eval(self.opener.open(req, data=urllib.urlencode(req_data)).read())
        total_data = return_data["data"]
        pages = return_data["pagination"]["pages"]
        for i in range(2, pages + 1):
            print i
            req_data["limit"] = i
            req_data["offset"] = req_data["offset"] + 10
            req = urllib2.Request(req_url, headers=self.headers)
            total_data += eval(self.opener.open(req, data=urllib.urlencode(req_data)).read())["data"]
            time.sleep(0.1)
        for i in total_data:
            print i

    def export_xconf_via_service_name(self, services, appid, token, app_name):
        """
        根据所有的service集合，导出所有的配置
        :param services: service集合
        :param appid: appid
        :param token: 导出需要放到data里面一个参数
        :return: 所有的配置信息
        """
        req_url = "http://%s/cnf/export" % (self.hosts[self.environment_name])
        del self.headers["token"]
        services_dict = {}
        for service in services:
            logging.info("servce: %s starts to export" % (service))
            req_data = {"token": token,
                        "downloadInfo": "%s,%s,%s" % (appid, self.environment_type_code, service)
                        }
            req = urllib2.Request(req_url, headers=self.headers)

            # with open("%s.conf" % (service), "wb") as File:
            #     contents = self.opener.open(req, data=urllib.urlencode(req_data)).read()
            #     print contents
            #     File.write(contents)
            # break
            services_dict[service] = {}
            contents = self.opener.open(req, data=urllib.urlencode(req_data)).read()
            for content in contents.split("\n")[:-1]:
                content = re.match("(.*?=.*)\#\#(.*)", content).groups()
                config = {}
                config_key = content[0].split("=")[0]
                config_value = content[0].split("=")[1]
                config["app_name"] = app_name  # 增加app name
                config["value"] = config_value
                config["description"] = content[1].strip()
                services_dict[service][config_key] = config
            logging.info("servce: %s ends to export" % (service))
        return services_dict

    def get_service_dict(self, app_name, cmp_name):
        """
        定义主函数
        :param app_name: 项目名称
        :return: 对应项目的所有service的配置
        """
        # self.environment_label = env_label
        self.add_token()
        appid = self.get_appid(app_name=app_name, cmp_name=cmp_name)
        if not appid:
            logging.error("appid is empty for %s" % (app_name))
            sys.exit(1)
        first_services = self.get_services(appid)
        if first_services:
            logging.info("services are : %s" % (str(first_services)))
        else:
            logging.error("services is empty for %s" % (app_name))
            sys.exit(1)
        # first_services = ['gateway-keeper'] # just for Debug
        service_dict = self.export_xconf_via_service_name(services=first_services, appid=appid,
                                                          token=self.headers["token"], app_name=app_name)
        return service_dict


class Compare(object):
    def __init__(self):
        pass

    def compare(self, first_environment_name, first_services_dict, second_environment_name,
                second_services_dict, ignore_leaked_service=False, ignore_leaked_configure=False):
        first_services = first_services_dict.keys()
        second_services = second_services_dict.keys()
        service_leak_from_second_services = set(first_services).difference(set(second_services))
        service_leak_from_first_services = set(second_services).difference(set(first_services))
        if service_leak_from_second_services or service_leak_from_first_services:
            print 'services are leaked from environment "%s": %s' % (second_environment_name,
                                                                     service_leak_from_second_services)
            print 'services are leaked from environment "%s": %s' % (first_environment_name,
                                                                     service_leak_from_first_services)
            if not ignore_leaked_service:
                return
        for service in set(first_services).intersection(set(second_services)):  # 取交集
            first_configures_form_service = first_services_dict[service]
            first_configures_form_service_key = first_configures_form_service.keys()
            second_configures_form_service = second_services_dict[service]
            second_configures_form_service_key = second_configures_form_service.keys()
            second_configures_from_service_leak = set(first_configures_form_service_key).difference(
                set(second_configures_form_service_key))
            first_configures_from_service_leak = set(second_configures_form_service_key).difference(
                set(first_configures_form_service_key))
            # second_configures_from_service_leak = [] # just for Debug
            # first_configures_from_service_leak = [] #just for Debug
            if second_configures_from_service_leak or first_configures_from_service_leak:
                print 'configures are leaked from service "%s" on environment "%s": %s' % (service,
                                                                                           second_environment_name,
                                                                                           second_configures_from_service_leak)
                print 'configures are leaked from service "%s" on environment "%s": %s' % (service,
                                                                                           first_environment_name,
                                                                                           first_configures_from_service_leak)
                if not ignore_leaked_configure:
                    return
            for configure in set(first_configures_form_service_key).intersection(
                    set(second_configures_form_service_key)):
                # print configure
                if first_services_dict[service][configure] != second_services_dict[service][configure]:
                    first_value = first_services_dict[service][configure]
                    second_value = second_services_dict[service][configure]
                    print 'configure is different for environment "%s" and environment "%s" on configure "%s" : %s | %s' % (
                        first_environment_name, second_environment_name, configure, first_value, second_value)


if __name__ == '__main__':
    # Xconf_a = GetXconf("product")
    # a_service_dict = Xconf_a.get_service_dict(app_name="zhengliang")
    Xconf_product = GetXconf("BetaD")
    print Xconf_product.sync_zk(app_name="loan-betad", cmp_name='zhenliang', service_name='loan-order-manage-service')
    # product_service_dict = Xconf_product.get_service_dict(app_name="loan-betad")
    # print product_service_dict
    # Compare = Compare()
    # Compare.compare("c", a_service_dict, "product", product_service_dict, ignore_leaked_service=True,
    #                 ignore_leaked_configure=True)
    # appid = a_CompareXconf.get_appid()
    # # CompareXconf.get_xconf(appid)
    # services = a_CompareXconf.get_services(appid)
    # a_services_dict = a_CompareXconf.export_xconf_via_service_name(services=services, appid=appid)
    # for services_dict_key in a_services_dict.keys():
    #     for service in a_services_dict[services_dict_key]:
    #         print services_dict_key, service

    # b_CompareXconf = CompareXconf("a")
    # appid = CompareXconf.get_appid()
    # # CompareXconf.get_xconf(appid)
    # services = CompareXconf.get_services(appid)
    # b_services_dict = CompareXconf.export_xconf_via_service_name(services=services, appid=appid)

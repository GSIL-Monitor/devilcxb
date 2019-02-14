# -*- coding:utf-8 -*-
import sys
import os
import time

if os.environ.get("WORKSPACE"):
    sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "AutoTest"))
from Tools.Common.MySQLHandle import MySQLHandle
import ConfigParser, os, re
import compareXconf
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class SyncXconfDataBetweenTwoEnv(object):
    def __init__(self, environment_name_a, environment_name_b, project, app_name, cmp_name, service_name=None,
                 commit=True):
        """
                初始化函数
        :param environment_name_a: 源环境
        :param environment_name_b: 目标环境
        :param project: 产品选，输入zhenliang, likai或者是sqlConf.int定义的产品线
        :param service_name: 需要同步的服务名称，如common服务，如果不选，则代表同步所有的服务
        :param app_name: 可传入多个app_name, 英文逗号隔开. 格式为task-schedule,loan-betae
        :param cmp_name: 字符类型， 一般为zhenliang
        """
        self.project = project
        self.environment_name_b = environment_name_b
        if self.environment_name_b == environment_name_a:
            logging.error("same env!!!!!!!!!!!!!!!!!")
            sys.exit("same env!!!!!!!!!!!!!!!!!")  # 检查是否传入相同的环境
        self.environment_name_a = environment_name_a
        self.config = ConfigParser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), self.project)
        config_file = os.path.join(self.config_path, 'config.ini')
        if os.path.isfile(config_file):
            logging.info("config file: %s" % (config_file))
        else:
            logging.error("config file is not existed: %s" % (config_file))
            sys.exit("config file is not existed: %s" % (config_file))
        self.config.read(config_file)
        # 构造sql_hosts字典，为了适配其他产品线，避免后续调用地方的更改
        sql_hosts = {}
        hosts_b = self.config.get(self.environment_name_b, "mysql_host")
        sql_hosts[self.environment_name_b] = [hosts_b.split(":")[0], int(hosts_b.split(":")[1])]
        self.service_name = service_name
        self.app_name = map(lambda x: x.strip(), app_name.split(","))
        if not self.app_name:
            logging.warning("app name is empty, please check!")
            sys.exit("app name is empty, please check!")
        self.cmp_name = cmp_name
        self.commit = commit
        # 先获取源环境的数据，如果不是生产环境，则从数据库里面获取xconf的配置
        if not self.environment_name_a == 'product':
            if self.config.has_option(self.environment_name_a, "mysql_schema"):
                schema = self.config.get(self.environment_name_a, "mysql_schema")
            else:
                schema = 'x_conf'
            hosts_a = self.config.get(self.environment_name_a, "mysql_host")
            sql_hosts[self.environment_name_a] = [hosts_a.split(":")[0], int(hosts_a.split(":")[1])]
            self.mysql_base_config_obj_a = MySQLHandle.MySqlHandle(host=sql_hosts[self.environment_name_a][0],
                                                                   port=sql_hosts[self.environment_name_a][1],
                                                                   username=self.config.get(self.environment_name_a,
                                                                                            "mysql_username"),
                                                                   password=self.config.get(self.environment_name_a,
                                                                                            "mysql_password"),
                                                                   schema=schema, return_dict=True)
            self.datas_from_a = self.get_data(self.mysql_base_config_obj_a)
            print len(self.datas_from_a)
        else:
            # 如果是生产环境，则采用urllib的方式去爬取数据。
            Xconf_product = compareXconf.GetXconf("product", project=self.project)
            product_service_dict = {}
            for app_name in self.app_name:
                service_dict_product_per_app_name = Xconf_product.get_service_dict(app_name, cmp_name=cmp_name)
                product_service_dict.update(service_dict_product_per_app_name)
            self.datas_from_a = []  # 转换为列表便于循环
            for service in product_service_dict.keys():
                for config in product_service_dict[service].keys():
                    self.datas_from_a.append(
                        {"app_name": product_service_dict[service][config]["app_name"], "server_name": service,
                         "key": config, "value": product_service_dict[service][config]["value"],
                         "config_remark": product_service_dict[service][config]["description"]})

        if self.config.has_option(self.environment_name_b, "mysql_schema"):
            schema = self.config.get(self.environment_name_b, "mysql_schema")
        else:
            schema = 'x_conf'
        logging.info("host: %s, port: %s, username: %s, passowrd: %s, schema: %s, is trying to connect!" % (
            sql_hosts[self.environment_name_b][0], sql_hosts[self.environment_name_b][1],
            self.config.get(self.environment_name_b,
                            "mysql_username"), self.config.get(self.environment_name_b,
                                                               "mysql_password"), schema))
        self.mysql_base_config_obj_b = MySQLHandle.MySqlHandle(host=sql_hosts[self.environment_name_b][0],
                                                               port=sql_hosts[self.environment_name_b][1],
                                                               username=self.config.get(self.environment_name_b,
                                                                                        "mysql_username"),
                                                               password=self.config.get(self.environment_name_b,
                                                                                        "mysql_password"),
                                                               schema=schema, return_dict=True)
        # GetXconf = compareXconf.GetXconf(self.environment_name_b[-1].lower())
        # GetXconf.add_token()
        # self.app_id_from_envrionment_b = GetXconf.get_appid()
        # print self.app_id_from_envrionment_b
        # 再获取目标环境的xconf配置，因为目标环境一定是可以通过sql获取到，所以直接通过查SQL的方式获取appid
        # self.app_id_from_envrionment_b = self.mysql_base_config_obj_b.execute_sql(
        #     "select app_id from app t where t.app_name='%s' and t.cmp_name='%s'" % (app_name, cmp_name))[0]["app_id"]
        self.app_ids_from_environment_b = self.mysql_base_config_obj_b.execute_sql(
            "select c.app_id, c.app_name from app c")
        if not self.app_ids_from_environment_b or len(self.app_ids_from_environment_b) != len(self.app_name):
            #   判断项目名称为空查询项目关联关系
            insert_cmp_name_sql = """INSERT  INTO `app`(`app_name`,`cmp_name`,`is_delete`,
                                            `create_time`,`update_time`,`create_by`,`update_by`) VALUES"""
            insert_cmp_name_tmpl_sql = """('{app_name}','{cmp_name}','1',
                                            '{now_time}','{now_time}',1,1),"""
            new_app_names = []
            for app_name_tmp in self.app_name:
                if self.app_ids_from_environment_b and app_name_tmp in [app_name_info.get('app_name') for
                                                                        app_name_info in
                                                                        self.app_ids_from_environment_b]:
                    continue
                insert_cmp_name_sql += insert_cmp_name_tmpl_sql.format(app_name=app_name_tmp,
                                                                       cmp_name=self.cmp_name,
                                                                       now_time=time.strftime(
                                                                           '%Y-%m-%d %H:%M:%S',
                                                                           time.localtime()))
                new_app_names.append(app_name_tmp)
            if new_app_names:
                self.mysql_base_config_obj_b.execute_sql(insert_cmp_name_sql[:-1])
                self.mysql_base_config_obj_b.commit()
                self.app_ids_from_environment_b = self.mysql_base_config_obj_b.execute_sql(
                    "select c.app_id, c.app_name from app c")
                insert_relations_sql = """INSERT INTO `user_app` 
                                               (`app_id`, `user_id`) VALUES """
                insert_relations_sql_tmpl = """ ('{app_id}', '1'),"""
                for app_tmp_info in self.app_ids_from_environment_b:
                    if app_tmp_info.get('app_name') in new_app_names:
                        insert_relations_sql += insert_relations_sql_tmpl.format(app_id=app_tmp_info.get('app_id'))
                self.mysql_base_config_obj_b.execute_sql(insert_relations_sql[:-1])
                self.mysql_base_config_obj_b.commit()

    def get_data(self, sql_obj):
        """
        获取xconf配置
        :param sql_obj: SQL对象
        :return: 返回SQL数据
        """
        # 如果不是生产环境，则通过数据库查询获取
        # if not self.environment_name_a == 'product':
        sql = "select c.*, t.app_name from app t, config c where t.app_name in (%s) and t.cmp_name='%s' and t.app_id=c.app_id" % (
            reduce(lambda x, y: x + "," + y, map(lambda x: "'" + x + "'", self.app_name)), self.cmp_name)
        if self.service_name:
            sql = sql + " and t.server_name='%s'" % (self.service_name)
        config_data = sql_obj.execute_sql(sql)
        # else:
        #     config_data = self.product_cofigures  # TODO： 此处有问题，后续处理
        return config_data

    def sync(self, server_name, key, value, remark, app_name=None):
        """
        同步xconf配置
        :param server_name: 服务名称，如common
        :param key: 配置名称
        :param value: 配置值
        :param remark: 配置的标注
        :return: None
        """
        value = value.replace('"', "'")  # 处理脏数据
        remark = remark.replace('"', "'")  # 处理脏数据
        remark = remark.replace("'", " ")  # 替换脏数据，避免更新数据时失败。
        white_items, white_items_for_service = self.get_white_items()
        white_items_for_service_values = []
        if white_items_for_service.values():
            white_items_for_service_values = reduce(lambda x, y: x + y, white_items_for_service.values())
        update_flag = False
        if server_name in white_items_for_service.keys():  # 用于处理不同的service拥有相同的配置项，但是只有其中一个服务的配置项设置了白名单。
            if key.lower() not in white_items_for_service[server_name]:
                update_flag = True
        else:
            update_flag = False
        # print self.mysql_base_config_obj_b.execute_sql("select * from config t where t.server_name='%s' and t.key='%s'" % (server_name, key))
        value_from_b = self.mysql_base_config_obj_b.execute_sql(
            "select * from config t where t.server_name='%s' and t.key='%s'" % (server_name, key))
        if value_from_b:
            value_from_b = value_from_b[0]
        # 2018-11-18 存在之前的bug会造成不同的环境用到的app_name是一样的，这样就导致之前的逻辑会找到错误的app_id_from_envrionment_b， 如在C环境找到loan-betae， 采用直接判断是否真量项目的逻辑来处理问题。
        if self.project != 'zhenliang':
            app_id_from_envrionment_b = filter(lambda x: x["app_name"] == app_name,
                                               self.app_ids_from_environment_b)
        else:
            # 适配真量，不同环境的app_name命名不一致的情况。
            app_id_from_envrionment_b = filter(lambda x: x["app_name"][:-1] == app_name[:-1],
                                               self.app_ids_from_environment_b)
        if not value_from_b:  # 如果目标不存在，则插入;或者对应服务的key不存在, 则同样插入
            if self.environment_name_a == "product":  # 如果是生产环境同步到测试环境，则所有邮件地址相关的都不同步，避免垃圾邮件发到业务人员。
                if re.match(".*@.*\.", value):
                    value = "someone@test.com"
            logging.info("key %s from service %s needs to insert" % (key, server_name))
            # print "INSERT INTO config (`server_name`, `key`, `value`, `config_remark`, `type`, `app_id`,`create_by`, `update_by`, `is_enable`, `is_delete`) VALUES ('%s', '%s', '%s', '%s', '2', '%s', '1', '1', '1', '1');" % (
            #         server_name, key, value,
            #         remark, app_id)
            if app_id_from_envrionment_b:
                app_name_from_envrionment_b = app_id_from_envrionment_b[0]["app_name"]
                app_id_from_envrionment_b = app_id_from_envrionment_b[0]["app_id"]
                self.mysql_base_config_obj_b.execute_sql(
                    'INSERT INTO config (`server_name`, `key`, `value`, `config_remark`, `type`, `app_id`,`create_by`, `update_by`, `is_enable`, `is_delete`) VALUES ("%s", "%s", "%s", "%s", "2", "%s", "1", "1", "1", "1");' % (
                        server_name, key, value,
                        remark, app_id_from_envrionment_b))
                return (app_name_from_envrionment_b, server_name)
            else:
                logging.warning("app_name: %s is not existed from des_env!" % (app_name))

        elif (key.lower() not in white_items + white_items_for_service_values) or update_flag:  # 判断是否为白名单配置，如果是， 则不处理
            if self.environment_name_a == "product":  # 如果是生产环境同步到测试环境，则所有邮件地址相关的都不同步，避免垃圾邮件发到业务人员。
                if re.match(".*@.*\.", value):
                    logging.warning("will not sync mail list from product to test!")
            # 2018-06-27， 修复数据库获取数据后的编码问题。
            if self.environment_name_a == "product":
                value_from_b_need_to_compare = value_from_b["value"].encode("utf-8")
            else:
                value_from_b_need_to_compare = value_from_b["value"]
            if value_from_b_need_to_compare != value:  # 如果两个环境的值不同，则更新目标环境的数据。
                logging.info("key %s from service %s needs to update" % (key, server_name))
                self.mysql_base_config_obj_b.execute_sql(
                    'update config t set t.value="%s" where t.server_name="%s" and t.key="%s"' % (
                        value, server_name, key))
                if app_id_from_envrionment_b:
                    app_name_from_envrionment_b = app_id_from_envrionment_b[0]["app_name"]
                    return (app_name_from_envrionment_b, server_name)
                else:
                    logging.warning("app_name: %s is not existed from des_env!" % (app_name))
            else:
                logging.info("key %s from service %s does not need to update" % (key, server_name))
        else:
            logging.info("key %s from service %s does not need to update" % (key, server_name))

    def get_white_items(self):
        """
        获取白名单配置， fixed_config.ini和dynamic_config.ini
        :return: 返回白名单配置
        """
        config = ConfigParser.ConfigParser()
        config.read([os.path.join(self.config_path, "fixed_config.ini"),
                     os.path.join(self.config_path, "dynamic_config.ini")])
        # 获取服务特有的白名单配置
        white_items_for_service = {}
        for service_name in config.sections():
            if service_name != "common":
                white_items_for_service[service_name] = map(lambda x: x[0].lower(), config.items(service_name))
        white_items = []
        if config.has_section("common"):
            white_items = map(lambda x: x[0].lower(), config.items("common"))
        return white_items, white_items_for_service

    def main(self):
        """
        主函数， 用于同步操作
        :return:
        """
        sync_zk_dict = {}
        if not self.datas_from_a:
            logging.warning("no data is found from %s" % (self.app_name))
        for data_from_a in self.datas_from_a:
            # print data_from_a
            sync_zk_result = self.sync(data_from_a["server_name"], data_from_a["key"], data_from_a["value"],
                                       data_from_a["config_remark"], app_name=data_from_a["app_name"])
            if sync_zk_result:
                if sync_zk_result[0] not in sync_zk_dict.keys():
                    sync_zk_dict[sync_zk_result[0]] = [sync_zk_result[1]]
                elif sync_zk_result[1] not in sync_zk_dict[sync_zk_result[0]]:
                    sync_zk_dict[sync_zk_result[0]].append(sync_zk_result[1])

        if self.commit == "true":
            self.mysql_base_config_obj_b.commit()
            # 2018/07/12: 发现同步到ZK的过程中，会出现根本没有改过的配置，暂时取消同步ZK操作。
            GetXconf_obj = compareXconf.GetXconf(self.environment_name_b, project=self.project)
            if not sync_zk_dict.keys():
                logging.info("no need to sync to zk!")
            else:
                for app_name in sync_zk_dict.keys():
                    for service_name in sync_zk_dict[app_name]:
                        if GetXconf_obj.sync_zk(app_name=app_name, cmp_name=self.cmp_name, service_name=service_name):
                            logging.info(
                                "cmp_name: %s, app_name: %s, service_name: %s is synced to zk successfully!" % (
                                    self.cmp_name, app_name, service_name))
                        else:
                            logging.error(
                                "cmp_name: %s, app_name: %s, service_name: %s is synced to zk failed!!!!!!!!!!!!!!!!!" % (
                                    self.cmp_name, app_name, service_name))
            params_file = os.path.join(os.environ.get("WORKSPACE"), "params.txt")
            if os.path.isfile(os.path.join(os.environ.get("WORKSPACE"), "params.txt")):
                os.remove(params_file)
            if self.project == 'zhenliang':
                File = open(params_file, "w")
                File.write("env=%s\n" % self.environment_name_b)
                File.write("cmp_name=%s\n" % self.project)
                File.write("app_name=loan-beta%s\n" % self.environment_name_b[-1].lower())
                File.close()

        else:
            logging.warning("will not commit to DB!!!!!!!!!!!!!!!")


if __name__ == '__main__':
    # SyncXconfDataBetweenTwoEnv = SyncXconfDataBetweenTwoEnv("BetaE", "BetaC", project="zhenliang",
    #                                                         app_name='loan-betae', cmp_name='zhenliang', commit='true')
    SyncXconfDataBetweenTwoEnv = SyncXconfDataBetweenTwoEnv(os.environ.get("src_env"), os.environ.get("des_env"),
                                                            project=os.environ.get("project"),
                                                            app_name=os.environ.get("app_name"),
                                                            cmp_name=os.environ.get("cmp_name"),
                                                            commit=os.environ.get("commit"))
    SyncXconfDataBetweenTwoEnv.main()

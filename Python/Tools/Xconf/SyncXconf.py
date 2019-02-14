# -*- coding:utf-8 -*-
import logging
from Tools.Common.MySQLHandle import MySQLHandle
import ConfigParser, os, re, sys


class SyncXconf(object):
    def __init__(self, environment_name):
        self.environment_name = environment_name
        self.environment_label = self.environment_name[-1].lower()
        # self.server_name = server_name
        sql_hosts = {"LoanBetaA": ["10.40.10.71", 3307],
                     "LoanBetaB": ["10.40.10.74", 3307],
                     "LoanBetaC": ["10.40.10.76", 3307],
                     "LoanBetaD": ["10.40.10.75", 3307],
                     "LoanBetaE": ["10.40.10.77", 3307]}
        self.mysql_base_config_obj = MySQLHandle.MySqlHandle(host=sql_hosts["LoanBetaA"][0],
                                                             port=sql_hosts["LoanBetaA"][1], username="api",
                                                             password="apipassword",
                                                             schema="x_conf")
        self.mysql_config_obj = MySQLHandle.MySqlHandle(host=sql_hosts[environment_name][0],
                                                        port=sql_hosts[environment_name][1], username="api",
                                                        password="apipassword",
                                                        schema="x_conf")
        self.orange = {"LoanBetaA": "10.40.11.61",
                       "LoanBetaB": "10.40.10.196",
                       "LoanBetaC": "10.40.11.167",
                       "LoanBetaD": "10.40.11.187",
                       "LoanBetaE": "10.40.11.195"}
        self.rocketmq = {"LoanBetaA": "10.40.10.82:9876",
                         "LoanBetaB": "10.40.10.202:9876",
                         "LoanBetaC": "10.40.10.168:9876",
                         "LoanBetaD": "10.40.10.169:9876",
                         "LoanBetaE": "10.40.10.62:9876"}
        self.ftp = {"LoanBetaA": "10.40.10.82:9876",
                    "LoanBetaB": "10.40.10.89",
                    "LoanBetaC": "10.40.10.168:9876",
                    "LoanBetaD": "10.40.10.10.40.10.83",
                    "LoanBetaE": "10.40.10.191"}  # 未处理

    def get_configures(self):
        sql = "select t.server_name, t.key, t.value, t.config_remark from config t"
        config_data = self.mysql_config_obj.execute_sql(sql)
        # config_data = map(lambda x: map(lambda y: y.encode("gbk"), x), config_data)
        return self.convert_to_dict(config_data)

    def get_server_pc_mapping_ip_and_port(self):
        sql = "select t.server_name, t.pc_ip, t.pc_port from ServerPcMapping t where t.server_group='%s'" % (
            self.environment_name)

        server_pc_mapping_ip_and_port_data = self.mysql_base_config_obj.execute_sql(sql)
        # server_pc_mapping_ip_and_port_data = map(lambda x: map(lambda y: y.encode("gbk"), x),
        #                                          server_pc_mapping_ip_and_port_data)
        return server_pc_mapping_ip_and_port_data

    def convert_to_dict(self, config_data):
        config_data_dict = {}
        for server_name, key, value, description in config_data:
            if server_name not in config_data_dict.keys():
                config_data_dict[server_name] = {key: {"value": value, "description": description}}
            else:
                config_data_dict[server_name][key] = {"value": value, "description": description}
        return config_data_dict

    def get_config_obj(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        # return config.items(section)
        return config

    def change_config_based_on_fixed_config(self, config_data, fixed_configures_obj, section="common"):
        for server in config_data.keys():
            for parameter in config_data[server].keys():
                if fixed_configures_obj.has_option(section, parameter):
                    base_parameter_value_from_config_file = fixed_configures_obj.get(section, parameter)
                    config_data[server][parameter]["value"] = base_parameter_value_from_config_file
        return config_data

    def get_cluster_value(self, re_expression, server_pc_mapping_ip_and_port_data):
        return reduce(lambda x, y: x + "," + y,
                      map(lambda x: x[1] + ":" + x[2],
                          filter(lambda x: re.match(re_expression, x[0]),
                                 server_pc_mapping_ip_and_port_data)))

    def change_config_based_on_dynamic_config(self, config_data, dynamic_configures_obj,
                                              server_pc_mapping_ip_and_port_data, section='common'):
        for server in config_data.keys():
            for parameter in config_data[server].keys():
                if dynamic_configures_obj.has_option(section, parameter):
                    base_parameter_value = dynamic_configures_obj.get(section, parameter).split("#")[0]
                    if parameter == "api.gateways":  # 配置orange网关地址
                        parameter_value = "%s:80" % (self.orange[self.environment_name])
                    elif parameter in ["spring.cloud.zookeeper.connectString", "zookeeper.addr", "zkCluster",
                                       "kafka.zk.cluster", "motan.registry.address"]:  # 配置zk集群地址
                        # print "2"
                        parameter_value = self.get_cluster_value("zk\w",
                                                                 server_pc_mapping_ip_and_port_data)
                    elif re.match("redis.node\d.host", parameter):  # 配置redis地址
                        # print "3"
                        parameter_value = \
                            filter(lambda x: re.match("redis\w", x[0]), server_pc_mapping_ip_and_port_data)[0][1]
                    elif re.search("mongodb.*host", parameter):  # 配置mongodb地址
                        # print "4"
                        parameter_value = \
                            filter(lambda x: re.match("mongodb\w", x[0]), server_pc_mapping_ip_and_port_data)[0][1]
                    elif parameter == 'mongo.db.hosts':  # 配置mongodb集群
                        # print "5"
                        parameter_value = self.get_cluster_value("mongodb\w",
                                                                 server_pc_mapping_ip_and_port_data)
                    elif parameter == 'redis.cluster.hosts':  # 配置redis集群
                        # print "6"
                        parameter_value = self.get_cluster_value("redis\w",
                                                                 server_pc_mapping_ip_and_port_data)
                        # print base_parameter_value
                    elif re.match("spring.datasource.druid.*", parameter):  # 配置mysql307
                        # print "7"
                        mysql_307 = filter(lambda x: x[0] == "307mysql", server_pc_mapping_ip_and_port_data)[0]
                        print "base_parameter_value: %s" % (base_parameter_value)
                        parameter_value = re.sub("//.*?/",
                                                 "//%s:%s/" % (mysql_307[1], mysql_307[2]),
                                                 base_parameter_value)
                        print "parameter_value: %s" % (parameter_value)
                    elif parameter in ["idNamePhoneCheck_url", "idNameCardNoCheck_url",
                                       "third.url"]:  # 配置profitcardthird
                        # print "8"
                        profitcardthird = \
                            filter(lambda x: x[0] == "profitcardthird", server_pc_mapping_ip_and_port_data)[0]
                        parameter_value = re.sub("//.*?/",
                                                 "//%s:%s/" % (
                                                     profitcardthird[1], profitcardthird[2]),
                                                 base_parameter_value)
                    elif parameter in ["bootstrap.servers", "kafka.borker.servers"]:  # 配置kafka集群
                        # print "9"
                        parameter_value = self.get_cluster_value("kafka\w",
                                                                 server_pc_mapping_ip_and_port_data)
                    elif re.match('http://\wzl', base_parameter_value):  # 替换环境标签
                        # print "10"
                        parameter_value = re.sub('//\wzl', "//%szl" % (self.environment_label), base_parameter_value)
                    elif re.match('http://beta\w"', base_parameter_value):  # 替换环境标签
                        # print "11"
                        parameter_value = re.sub('//beta\w', "//beta%s" % (self.environment_label),
                                                 base_parameter_value)
                    elif re.match("http://\wlk", base_parameter_value):  # 替换环境标签
                        # print "12"
                        parameter_value = re.sub('//\wlk', "//%slk" % (self.environment_label), base_parameter_value)
                    elif parameter == "spring.cloud.zookeeper.discovery.instanceHost":  # 配置profitcardthird IP
                        # print "13"
                        profitcardthird = \
                            filter(lambda x: x[0] == "profitcardthird", server_pc_mapping_ip_and_port_data)[0]
                        parameter_value = profitcardthird[1]
                    elif parameter == "acl-ips":  # 配置acl-ips
                        # print "14"
                        ips = reduce(lambda x, y: x + "," + y, map(lambda x: "%s/32" % (x), list(
                            set(map(lambda x: x[1], server_pc_mapping_ip_and_port_data)))))
                        parameter_value = ips
                    elif parameter == "xxl.job.admin.addresses":  # xxl.job.admin.addresses
                        # print "15"
                        try:
                            loanopenapi = filter(lambda x: x[0] == "loanopenapi", server_pc_mapping_ip_and_port_data)[0]
                            parameter_value = re.sub("//.*?/",
                                                     "//%s:%s/" % (loanopenapi[1], loanopenapi[2]),
                                                     base_parameter_value)
                        except:
                            pass
                    elif parameter == "zl.name.server.address":  # 替换MQ地址
                        parameter_value = self.rocketmq[self.environment_name]
                    # FTP地址暂时未作使用
                    # elif parameter == "ftp.address":  # 替换FTP地址
                    #     parameter_value = self.rocketmq[self.environment_name]
                    elif parameter == 'spring.cloud.zookeeper.discovery.root':
                        parameter_value = re.sub('beta\w', "beta%s" % (self.environment_label),
                                                 base_parameter_value)
                    if not parameter_value:
                        sys.exit("%s is not matched" % (base_parameter_value))
                    # print base_parameter_value
                    # print parameter_value
                    config_data[server][parameter]["value"] = parameter_value

        return config_data

    def update_config(self, service_name, key, value):
        print "update config t set t.value='%s' where t.server_name='%s' and t.key='%s'" % (value, service_name, key)
        self.mysql_config_obj.execute_sql(
            "update config t set t.value='%s' where t.server_name='%s' and t.key='%s'" % (value, service_name, key))

    def main(self):
        config_data = self.get_configures()
        config_data_old = str(config_data)
        config_path = os.path.join(os.path.dirname(__file__), "zhenliang")
        fixed_configures_obj = self.get_config_obj(os.path.join(config_path, "fixed_config.ini"))
        dynamic_configures_obj = self.get_config_obj(os.path.join(config_path, "dynamic_config.ini"))
        server_pc_mapping_ip_and_port_data = self.get_server_pc_mapping_ip_and_port()
        config_data = self.change_config_based_on_fixed_config(config_data, fixed_configures_obj)
        print config_data
        config_data_new = self.change_config_based_on_dynamic_config(config_data=config_data,
                                                                     dynamic_configures_obj=dynamic_configures_obj,
                                                                     server_pc_mapping_ip_and_port_data=server_pc_mapping_ip_and_port_data,
                                                                     section='common')
        print config_data_new
        config_data_old = eval(config_data_old)
        for key in config_data_old.keys():
            for sub_key in config_data_old[key].keys():
                if config_data_old[key][sub_key]["value"] != config_data_new[key][sub_key]["value"]:
                    print key
                    print sub_key
                    print config_data_old[key][sub_key]["value"]
                    print config_data_new[key][sub_key]["value"]
                    self.update_config(key, sub_key, config_data_new[key][sub_key]["value"])
        self.mysql_config_obj.commit()
        self.mysql_config_obj.close()
        self.mysql_base_config_obj.close()


if __name__ == '__main__':
    SyncXconf = SyncXconf("LoanBetaD")
    SyncXconf.main()

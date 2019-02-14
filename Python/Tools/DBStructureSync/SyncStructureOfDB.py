# -*- coding:utf-8 -*-
import sys
import os
from ImportDBStructureFromPRDToPP import ImportDBStructureFromPRDToPP

sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "AutoTest"))
from Tools.Common.TelnetHandle import TelnetHandle
import ConfigParser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class SyncStrucTrueOfDB(object):
    def __init__(self, project, environment_name_a, environment_name_b, schemas, label=None, commit=''):
        if environment_name_b == environment_name_a:
            logging.error("same env!!!!!!!!!!!!!!!!!")
            sys.exit("same env!!!!!!!!!!!!!!!!!")  # 检查是否传入相同的环境
        self.commit = commit
        self.environment_name_a = environment_name_a
        self.environment_name_b = environment_name_b
        if self.environment_name_a == 'product':
            if not label:
                logging.error("please specify the label to fetch the sql file from 174!")
                sys.exit("please specify the label to fetch the sql file from 174!")
            ImportDBStructureFromPRDToPP_obj = ImportDBStructureFromPRDToPP(project=project, label=label)
            ImportDBStructureFromPRDToPP_obj.main()
        self.schemas = schemas
        self.python_schema_path = "/usr/local/bin/python2.7 /usr/local/lib/python2.7/site-packages/schemasync/schemasync.py"
        # self.python_schema_path = "schemasync"
        self.config = ConfigParser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), project)
        config_file = os.path.join(self.config_path, 'config.ini')
        if os.path.isfile(config_file):
            logging.info("config file: %s" % (config_file))
        else:
            logging.error("config file is not existed: %s" % (config_file))
            sys.exit("config file is not existed: %s" % (config_file))
        self.config.read(config_file)

    def get_telnet(self):
        """
        获取telnet客户端
        :return:
        """
        common_config = ConfigParser.ConfigParser()
        common_config_path = os.path.join(os.path.dirname(__file__), "common")
        common_config_file = os.path.join(common_config_path, 'config.ini')
        common_config.read(common_config_file)
        tn = TelnetHandle.TelnetHandle(host=common_config.get("telnet", "host"),
                                       username=common_config.get("telnet", "username"),
                                       password=common_config.get("telnet", "password"))
        return tn

    def change_sql_file(self, sql_file):
        contents = open(sql_file).readlines()
        count = 0
        delete_different_table = os.environ.get("delete_different_table")
        while count < len(contents):
            if "NULL DEFAULT AFTER" in contents[count]:
                contents[count] = contents[count].replace("NULL DEFAULT AFTER",
                                                          "NULL DEFAULT NULL AFTER")  # 适配NULL DEFAULT AFTER会报错的问题
            # 20181221 	是否删除目标环境存在而源环境不存在的表。如还在功能测试环节，这个是否同步预生产环境的表结构到功能测试环境，就不应该删除功能测试环境的表。
            if "DROP" in contents[count]:
                if delete_different_table == 'false':
                    contents[count] = "--" + contents[count]
            # 20190104：暂时强制规避中文问题。
            if "h5_support" in contents[count]:
                contents[count] = "--" + contents[count]
            count += 1
        open(sql_file, "w").writelines(contents)

    def dump_sql_file(self):
        if self.environment_name_a == "product":  # 适配生产同步到PP
            env_a_host = self.config.get("PP", "mysql_host").split(":")[0]
            env_a_port = int(self.config.get("PP", "mysql_host").split(":")[1])
            env_a_username = self.config.get("PP", "mysql_username")
            env_a_password = self.config.get("PP", "mysql_password")
        else:
            env_a_host = self.config.get(self.environment_name_a, "mysql_host").split(":")[0]
            env_a_port = int(self.config.get(self.environment_name_a, "mysql_host").split(":")[1])
            env_a_username = self.config.get(self.environment_name_a, "mysql_username")
            env_a_password = self.config.get(self.environment_name_a, "mysql_password")
        env_b_host = self.config.get(self.environment_name_b, "mysql_host").split(":")[0]
        env_b_port = int(self.config.get(self.environment_name_b, "mysql_host").split(":")[1])
        env_b_username = self.config.get(self.environment_name_b, "mysql_username")
        env_b_password = self.config.get(self.environment_name_b, "mysql_password")
        cur_path = os.environ.get("WORKSPACE")
        # cur_path = os.path.dirname(__file__)
        for schema in map(lambda x: x.strip(), self.schemas.split(",")):
            if self.environment_name_a == "product":  # 适配生产同步到PP
                schema_bak = schema + "_bak"
            else:
                schema_bak = schema
            logging.info('%s --output-directory=%s mysql://%s:%s@%s:%d/%s  mysql://%s:%s@%s:%d/%s' % (
                self.python_schema_path, cur_path,
                env_a_username, env_a_password,
                env_a_host,
                env_a_port, schema_bak, env_b_username,
                env_b_password,
                env_b_host, env_b_port, schema))
            os.system('%s --output-directory=%s mysql://%s:%s@%s:%d/%s  mysql://%s:%s@%s:%d/%s' % (
                self.python_schema_path, cur_path,
                env_a_username, env_a_password,
                env_a_host,
                env_a_port, schema_bak, env_b_username,
                env_b_password,
                env_b_host, env_b_port, schema))

        logging.info('mysql -h%s -u%s -p%s -P%d --default-character-set=utf8' % (
            env_b_host, env_b_username, env_b_password, env_b_port))
        sql_files = filter(lambda x: x.endswith(".patch.sql"), os.listdir(cur_path))
        for sql_file in sql_files:
            self.change_sql_file(os.path.join(cur_path, sql_file)) #20180828: 适配NULL DEFAULT AFTER
        if not sql_files:
            logging.error("patch.sql is missed, please check if wrong db name is specified: %s!" % (self.schemas))
            sys.exit("patch.sql is missed, please check if wrong db name is specified: %s!" % (self.schemas))
        sql_all_file = os.path.join(cur_path, "source_all.sql")
        open(sql_all_file, "w").writelines(
            map(lambda x: "source %s\n" % (x), sql_files))
        tn = self.get_telnet()
        tn.exe_cmd("cd %s" % (cur_path), "# ")
        tn.exe_cmd('mysql -h%s -u%s -p%s -P%d --default-character-set=utf8' % (
            env_b_host, env_b_username, env_b_password, env_b_port), "mysql> ")
        logging.info("source %s" % (sql_all_file))
        if self.commit == 'true':
            result = tn.exe_cmd("source %s" % (sql_all_file), "mysql> ", timeout=50)
        else:
            logging.warning("will not sync since commit is not checked!")
        tn.close_telnet()

    def main(self):
        self.dump_sql_file()


if __name__ == '__main__':
    # SyncStrucTrueOfDB = SyncStrucTrueOfDB("zhenliang", "BetaA", "BetaE", "xd_business, xd_p2p")
    SyncStrucTrueOfDB = SyncStrucTrueOfDB(project=os.environ.get("project"),
                                          environment_name_a=os.environ.get("src_env"),
                                          environment_name_b=os.environ.get("des_env"),
                                          schemas=os.environ.get("schemas"), label=os.environ.get("label"),
                                          commit=os.environ.get("commit"))
    SyncStrucTrueOfDB.main()

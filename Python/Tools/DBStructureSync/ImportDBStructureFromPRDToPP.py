# -*- coding:utf-8 -*-
import sys
import os

sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "AutoTest"))
from Tools.Common.SSHHandle import SSHHandle
from Tools.Common.TelnetHandle import TelnetHandle
import shutil
import tarfile
from subprocess import *
import re
import ConfigParser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class ImportDBStructureFromPRDToPP(object):
    def __init__(self, project, label):
        self.project_name = project
        self.common_config = self.get_common_cofig_obj()
        self.project_config = self.get_project_cofig_obj()
        self.ssh_client = self.get_ssh_client()
        self.src_path = self.common_config.get("prd_db_ssh", "src_path")
        self.label = label
        self.des_path = os.environ.get("WORKSPACE")
        # self.des_path = os.path.dirname(__file__)

    def get_common_cofig_obj(self):
        """
        获取config的对象
        :return:
        """
        common_config = ConfigParser.ConfigParser()
        common_config_path = os.path.join(os.path.dirname(__file__), "common")
        common_config_file = os.path.join(common_config_path, 'config.ini')
        if not os.path.isfile(common_config_file):
            logging.error("%s is not existed!" % (common_config_file))
            sys.exit("%s is not existed!" % (common_config_file))
        common_config.read(common_config_file)
        return common_config

    def get_project_cofig_obj(self):
        """
        获取项目config的对象
        :return:
        """
        project_config = ConfigParser.ConfigParser()
        project_config_path = os.path.join(os.path.dirname(__file__), self.project_name)
        project_config_file = os.path.join(project_config_path, 'config.ini')
        if not os.path.isfile(project_config_file):
            logging.error("%s is not existed!" % (project_config_file))
            sys.exit("%s is not existed!" % (project_config_file))
        project_config.read(project_config_file)
        return project_config

    def get_ssh_client(self):
        """
        获取ssh客户端
        :return:
        """
        ssh_client = SSHHandle.HandleSSH(host=self.common_config.get("prd_db_ssh", "host"),
                                         username=self.common_config.get("prd_db_ssh", "username"),
                                         password=self.common_config.get("prd_db_ssh", "password"),
                                         port=int(self.common_config.get("prd_db_ssh", "port")))
        return ssh_client

    def copy_file(self):
        """
        根据每个项目不同的标签远程拷贝打包好的数据库文件到当前的目录
        :return: 拷贝完成的文件目录
        """
        files = self.ssh_client.execute_command("ls %s" % (self.src_path))
        if not filter(lambda x: self.label in x, files):
            logging.error("sql file is not existed via label: %s" % (self.label))
            sys.exit("sql file is not existed via label: %s" % (self.label))
        zl_db_structure_file = filter(lambda x: self.label in x, files)[0].strip()
        if zl_db_structure_file:
            des_file = os.path.join(self.des_path, zl_db_structure_file)
            if not os.path.isfile(des_file):
                logging.info("src file: %s" % (os.path.join(self.src_path, zl_db_structure_file)))
                logging.info("des file: %s" % (des_file))
                self.ssh_client.get_file_via_sftp(os.path.join(self.src_path, zl_db_structure_file), des_file)
            else:
                logging.warning("%s is handled already!" % (zl_db_structure_file))
            return des_file
        else:
            logging.error("%s is not existed, please check manually!" % (zl_db_structure_file))
        self.ssh_client.close_client_connection()

    def walk(self, path):
        """
        遍历所有文件
        :param path: 路径
        :return:
        """
        if not os.path.exists(path):
            return -1
        for root, dirs, names in os.walk(path):
            for filename in names:
                if filename == "schema.sql":
                    return os.path.join(root, filename)

    def un_tar(self, file_name):
        """
        解压获取到的压缩包
        :param file_name: 本地的压缩包文件
        :return:
        """
        tar = tarfile.open(file_name)
        names = tar.getnames()
        if os.path.isdir(file_name + "_files"):
            pass
        else:
            os.mkdir(file_name + "_files")
        # 因为解压后是很多文件，预先建立同名目录
        for name in names:
            tar.extract(name, file_name + "_files/")
        tar.close()
        sql_file = self.walk(file_name + "_files/")
        if sql_file:
            print "%s is found and will be used to dump!" % (sql_file)
        return sql_file

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

    def change_schema_name(self, sql_file):
        """
        改变数据库的库名称，用于存于PP
        :param sql_file: SQL文件
        :return:
        """
        contents = open(sql_file).readlines()
        count = 0
        while count < len(contents):
            if re.search("CREATE DATABASE.*?`.*?` /", contents[count]):
                schema = re.findall("CREATE DATABASE.*?`(\w+)?`", contents[count])[0]
                logging.info(
                    "%s is changed to: %s" % (contents[count], contents[count].replace(schema, schema + "_bak")))
                contents[count] = contents[count].replace(schema, schema + "_bak")
            elif re.search("USE `.*?`;", contents[count]):
                schema = re.findall("USE `(\w+)?`;", contents[count])[0].replace("'", "")
                contents[count] = contents[count].replace(schema, schema + "_bak")
                logging.info(
                    "%s is changed to: %s" % (contents[count], contents[count].replace(schema, schema + "_bak")))
            count += 1
        open(sql_file, "w").writelines(contents)
        return sql_file

    def dump_sql_file(self, sql_file):
        tn = self.get_telnet()
        tn.exe_cmd("cd %s" % (self.des_path), "# ")
        logging.info('mysql -h%s -u%s -p%s -P%d --default-character-set=utf8' % (
            self.project_config.get("PP", "mysql_host").split(":")[0], self.project_config.get("PP", "mysql_username"),
            self.project_config.get("PP", "mysql_password"),
            int(self.project_config.get("PP", "mysql_host").split(":")[1])))
        tn.exe_cmd('mysql -h%s -u%s -p%s -P%d --default-character-set=utf8' % (
            self.project_config.get("PP", "mysql_host").split(":")[0], self.project_config.get("PP", "mysql_username"),
            self.project_config.get("PP", "mysql_password"),
            int(self.project_config.get("PP", "mysql_host").split(":")[1])), "mysql> ")
        logging.info("source %s" % (sql_file))
        result = tn.exe_cmd("source %s" % (sql_file), "mysql> ", timeout=50)
        tn.close_telnet()

    def main(self):
        des_file = self.copy_file()
        sql_file = self.un_tar(des_file)
        # sql_file = r"E:\Testing_Repository\AutoTest\Tools\Common\Xconf\schema.sql"
        sql_file = self.change_schema_name(sql_file)
        self.dump_sql_file(sql_file)


# if __name__ == '__main__':
#     ImportDBStructureFromPRDToPP = ImportDBStructureFromPRDToPP(project="zhenliang", label="zlxd_")
#     ImportDBStructureFromPRDToPP.main()

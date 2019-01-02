# -*- coding: utf-8 -*-
import paramiko
import logging
logging.basicConfig(level=logging.INFO)


class HandleSSH(object):
    def __init__(self, host, username, password, port=22):
        """
        初始化ssh连接
        :param host: IP地址
        :param username: 用户名
        :param password: 密码
        :param port: 端口号，默认为22
        :return: None
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, port, username, password)
        logging.info("ssh connection is established!")

    def execute_command(self, command):
        """
        执行命令
        :param command: 命令
        :return: 执行结果
        """
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.readlines()

    def close_client_connection(self):
        """
        关闭ssh连接
        :return: None
        """
        self.ssh.close()

if __name__ == "__main__":
    HandleSSH = HandleSSH("10.115.101.230:8080", "xiaobo.chi", "123456")
    HandleSSH.execute_command("ls")
    HandleSSH.close_client_connection()
# -*- coding:utf-8 -*-
# Auther: Chi Xiaobo
# 2018.04.17: first draft
import paramiko
import os
import re


def add_user(session_path, username, password):
    hosts = get_hosts(session_path, username)
    for host in hosts:
        try:
            # 创建SSH对象
            ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            ssh.connect(hostname=host[0], port=host[1], username='root', password='@6ePB#ms@)!&yooli!@!^')
            # 执行命令
            stdin, stdout, stderr = ssh.exec_command('useradd -g QA  {}'.format(username))
            stdin, stdout, stderr = ssh.exec_command('echo {}:{} | chpasswd'.format(username, password))
            # 获取命令结果
            # 关闭连接
            ssh.close()
        except Exception as msg:
            print str(msg)


def change_username_from_session_file(session_file, username):
    contents = open(session_file).readlines()
    for i in range(len(contents)):
        if re.match("UserName=.*", contents[i]):
            contents[i] = "UserName={}\n".format(username)
    open(session_file, "w").writelines(contents)


def get_hosts(session_path, username):
    # src_path = r"C:\Users\Administrator\Documents\NetSarang\Xshell\Sessions"
    hosts = []
    for root, dirs, files in os.walk(session_path):
        # for dir in dirs:
        #     print(os.path.join(root, dir))
        for File in files:
            if File.endswith(".xsh"):
                file_path = os.path.join(root, File)
                contents = open(file_path).readlines()
                host = filter(lambda x: re.match("Host=10.*", x), contents)[0].split("=")[1].strip()
                port = filter(lambda x: re.match("Port=.*", x), contents)[0].split("=")[1].strip()
                hosts.append((host, port))
                change_username_from_session_file(file_path, username)

    return hosts


if __name__ == '__main__':
    add_user(session_path=r"C:\Users\Administrator\Documents\NetSarang\Xshell\Sessions", username="chixiaobo",
             password="DEVIL_cxb123")

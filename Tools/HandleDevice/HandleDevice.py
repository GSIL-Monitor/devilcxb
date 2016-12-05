# -*- coding: utf-8 -*-
import logging
import os
import sys
import re
import subprocess
from subprocess import STDOUT, check_output
import time
import datetime
import ConfigParser
logging.basicConfig(level=logging.INFO)


class HandleDevice(object):
    def __init__(self):
        pass

    def execute_cmd(self, cmd, timeout=60):
        """
        执行cmd命令
        :param cmd: 需要执行cmd命令
        :return: 返回执行结果
        """
        data = subprocess.Popen(cmd, bufsize=1024, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if data.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                data.terminate()
                logging.warning("execute " + cmd + "timeout after " + str(timeout) + "seconds!")
                if re.findall("adb -s \w+", cmd) and not re.findall("adb -s \w+ reboot", cmd):
                    self.reboot_device(re.findall("adb -s (\w+)", cmd)[0])
                exe = os.popen(cmd)
                return exe.readlines()
            time.sleep(0.1)
        info = data.stdout.readlines()
        # 20161114: Try to release the memory.
        if data.stdin:
            data.stdin.close()
        if data.stdout:
            data.stdout.close()
        if data.stderr:
            data.stderr.close()
        try:
            data.kill()
        except OSError:
            pass
        return info

    def reboot_device(self, deviceid):
        """
        reboot device
        :param deviceid:
        :return: None
        """
        self.execute_cmd("adb -s " + deviceid + " reboot", timeout=30)

    def get_devices_info(self):
        """
        用于获取所有手机的唯一标识
        :return: 手机的唯一标识
        """
        return map(lambda x: x.replace("\tdevice\r\n", ""),
                   filter(lambda x: re.search(".*\tdevice\r\n", x), self.execute_cmd("adb devices")))

    def get_product_info(self, deviceid):
        """
        用于获取手机的类型，如Pixi4-6_4G
        :param deviceid: 传入的手机唯一标识，通过adb devices的方式获取
        :return: 手机类型，如Pixi4-6_4G
        """
        try:
            return \
                re.findall("\[(.*?\])",
                           self.execute_cmd('adb -s ' + deviceid + ' shell getprop | find "ro.build.product"')[0])[
                    1].replace("]", "")
        except:
            return \
                        re.findall("\[(.*?\])",
                                   self.execute_cmd('adb -s ' + deviceid + ' shell getprop | find "ro.build.product"')[0])[
                            1].replace("]", "")

    def get_model_number(self, deviceid):
        """
        用于获取手机的model号，如4072D
        :param deviceid: 传入的手机唯一标识，通过adb devices的方式获取
        :return: 手机的model号，如4072D
        """
        try:
            model_number = self.execute_cmd("adb -s " + deviceid + ' shell getprop ro.product.model')[0].strip()
        except:
            model_number = self.execute_cmd("adb -s " + deviceid + ' shell getprop ro.product.model')[0].strip()
        if model_number:
            return model_number
        return ""

    def get_device_platform_version(self, deviceid):
        """
        用于获取手机的Android 版本，如6.0.1
        :param deviceid:传入的手机唯一标识，通过adb devices的方式获取
        :return:手机的Android 版本，如6.0.1
        """
        try:
            platform_version = self.execute_cmd("adb -s " + deviceid + " shell getprop ro.build.version.release")[0].strip()
        except:
            platform_version = self.execute_cmd("adb -s " + deviceid + " shell getprop ro.build.version.release")[0].strip()
        if re.search("\d+\.\d+\.\d+", platform_version):
            return platform_version
        elif re.search("\d+\.\d+", platform_version):
            return platform_version + ".0"
        return ""

    def get_device_resolution(self, deviceid):
        """
        获取设备分辨率
        :param deviceid:  设备号
        :return: 分辨率
        """
        try:
            solution_result = self.execute_cmd('adb -s ' + deviceid + ' shell dumpsys window windows | find "Frames:"')
        except:
            solution_result = self.execute_cmd('adb -s ' + deviceid + ' shell dumpsys window windows | find "Frames:"')
        if solution_result:
            return re.findall(".*\]\[(\d+,\d+)\]", solution_result[0])[0].replace(",", "*")
        return ""

    def get_keyword_values(self, data, keyword):
        """
        返回字典里面的关键字的值
        :param data: 字典或者列表嵌套字典类型
        :param keyword: 关键字
        :return: 返回关键字的值
        """
        if type(data) == dict:
            return data[keyword]
        elif type(data) == list:
            return map(lambda x: x[keyword], data)

    def GetJenkinsVar(self, key):
        """
        获取构建jenkins job时的参数值
        :param key: 参数名称
        :return: 参数值
        """
        try:
            value = os.environ.get(key)
        except Exception:
            value = os.environ.get(key.upper())
        #print('value = ',value)
        if(not value):
            value = ''
        #print( os.path.join(r'c:/a',value) )
        return value

    def get_battery_level(self, deviceID):
        """
        获取手机的电量
        :param deviceID: 手机ID
        :return: 电量
        """
        try:
            batteryLevel = int(re.findall("level: (\d+)", self.execute_cmd("adb -s " + deviceID + ' shell dumpsys battery | find "level"')[0])[0])
        except:
            batteryLevel = 84
        return batteryLevel

    def kill_process(self, conditions):
        """
        通过netstat查到Slave占用的进程，并结束掉
        :param conditions: 查询的条件
        :return: None
        """
        cmd_result = self.execute_cmd('netstat -ano | find "' + conditions + '"')
        if cmd_result:
            pid = cmd_result[0].strip().split()[-1]
            self.execute_cmd("taskkill /F /PID " + pid)
            logging.info(pid + " is killed with " + conditions + " as the conditions!")

    def handle_node_online(self, HandleJenkins, node_name, HandleMongoDB, pcInfo_table_obj, deviceInfo_table_ojb, deviceInfo_table_projectMapping_ojb):
        """
        20160712: 解决端口使用异常
        当Slave启动异常时，尝试做修复性的操作，并抛弃当前的端口
        20160712： 解决安全性测试节点变动问题
        当检测为安全性测试的设备时，取消在设备表的删除操作
        :param HandleJenkins: HandleJenkins的实例对象
        :param node_name: 节点名称
        :param HandleMongoDB: HandleMongoDB的实例对象
        :param pcInfo_table_obj: pc信息表的monggodb表对象
        :param deviceInfo_table_ojb: 设备信息表的monggodb表对象
        :param deviceInfo_table_projectMapping_ojb: 项目信息表的monggodb表对象
        :return: None
        """
        try:
            HandleJenkins.online_node(node_name)
        except Exception as e:
            if e.message == "Node is offline and not marked as temporarilyOffline, check client connection: offline = True, temporarilyOffline = False":
                logging.warning("Node is online failed since the task is launched failed on PC!")
                max_jenkins_port = HandleMongoDB.query_table(pcInfo_table_obj, {"max_jenkins_port": {"$exists": True}}, {"max_jenkins_port": 1})[0]["max_jenkins_port"]
                if not HandleMongoDB.query_table(deviceInfo_table_ojb, {"nodeName": node_name}):
                    HandleMongoDB.update_item(pcInfo_table_obj, {"max_jenkins_port": max_jenkins_port}, {"max_jenkins_port": max_jenkins_port + 1})
                # else:
                    #if not HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": node_name.split("_")[-1], "project": {"$in": ["security", "monkey"]}}):
                    # HandleMongoDB.delete_items(deviceInfo_table_ojb, {"nodeName": node_name})

    def close_invalid_connection(self, jenkins_ip):
        """
        Close invalid connection
        :return: None
        """
        data = subprocess.Popen("netstat -ano", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        info = data.stdout.readlines()
        # print info
        invalid_connection = filter(lambda x: re.search(".*" + jenkins_ip + ":.*\d+.*CLOSE_WAIT", x), info)
        if invalid_connection:
            pids = map(lambda x: x.strip().split()[-1], invalid_connection)
            for pid in pids:
                os.system("taskkill /F /PID " + pid)

    def get_running_pid(self, nodeName, jenkins_server_address):
        """
        因为Jenkins升级，导致所有的Slave连接jenkins都是同一个TCP端口，所有没办法跟踪PID
        :param nodeName: 节点名称
        :return: PID
        """
        print nodeName
        print jenkins_server_address
        logging.info('netstat -ano | find "' + jenkins_server_address + ':"')
        try:
            before_pid =  map(lambda x: x.strip().split()[-1], filter(lambda x: "ESTABLISHED" in x, self.execute_cmd('netstat -ano | find "' + jenkins_server_address + ':"', 90)))
        except TypeError:
            before_pid =  map(lambda x: x.strip().split()[-1], filter(lambda x: "ESTABLISHED" in x, self.execute_cmd('netstat -ano | find "' + jenkins_server_address + ':"', 90)))
        print before_pid
        self.execute_cmd("schtasks /Run /TN " + nodeName)
        time.sleep(40)
        try:
            after_pid = map(lambda x: x.strip().split()[-1], filter(lambda x: "ESTABLISHED" in x, self.execute_cmd('netstat -ano | find "' + jenkins_server_address + ':"', 90)))
        except TypeError:
            after_pid = map(lambda x: x.strip().split()[-1], filter(lambda x: "ESTABLISHED" in x, self.execute_cmd('netstat -ano | find "' + jenkins_server_address + ':"', 90)))
        print after_pid
        if before_pid == after_pid:
            return self.get_running_pid(nodeName, jenkins_server_address)
        return list(set(after_pid).difference(set(before_pid)))[0]

    def main(self):
        logging.info("********************starting********************")
        logging.info(os.path.join(self.GetJenkinsVar("WORKSPACE"), "SVN"))
        sys.path.append(os.path.join(self.GetJenkinsVar("WORKSPACE"), "SVN"))
        devices_id = self.get_devices_info()
        # 2016/11/28 try again to get devices
        if not devices_id:
           devices_id = self.get_devices_info()
        logging.info("devices id: " + str(devices_id))
        config = ConfigParser.ConfigParser()
        logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        based_node_name = self.GetJenkinsVar("nodeName")
        logging.info("##################Mongodb connection########################")
        from Tools.HandleMongoDB.HandleMongoDB import HandleMongoDB
        host = config.get("config_mongodb", "host")
        port = int(config.get("config_mongodb", "port"))
        Device_db = config.get("config_mongodb", "database")
        deviceInfo_table = config.get("config_mongodb", "table")
        pcInfo_table = config.get("config_mongodb", "table_pcInfo")
        deviceInfo_table_projectMapping = config.get("config_mongodb", "table_projectMapping")
        HandleMongoDB = HandleMongoDB(host, port)
        db_obj = HandleMongoDB.get_db(Device_db)
        deviceInfo_table_ojb = HandleMongoDB.get_table(db_obj, deviceInfo_table)
        deviceInfo_table_projectMapping_ojb = HandleMongoDB.get_table(db_obj, deviceInfo_table_projectMapping)
        pcInfo_table_obj = HandleMongoDB.get_table(db_obj, pcInfo_table)
        logging.info("##########################SSH connection######################")
        """
        from Tools.HandleSSH.HandleSSH import HandleSSH
        ssh_host = config.get("config_ssh", "host")
        ssh_port = int(config.get("config_ssh", "port"))
        ssh_username = config.get("config_ssh", "username")
        ssh_password = config.get("config_ssh", "password")
        ssh_jenkins_host = config.get("config_ssh", "jenkins_host")
        HandleSSH = HandleSSH(ssh_host, ssh_username, ssh_password, ssh_port)
        """
        logging.info("######################Jenkins connection########################")
        from Tools.HandleJenkins.HandleJenkins import HandleJenkins
        jenkins_server = config.get("config_jenkins", "server")
        jenkins_ip = re.findall(".*//(\d+\.\d+\.\d+\.\d+)", jenkins_server)[0]
        jenkins_username = config.get("config_jenkins", "username")
        jenkins_password = config.get("config_jenkins", "password")
        HandleJenkins = HandleJenkins(jenkins_server, jenkins_username, jenkins_password)
        logging.info("######################SQLdb connection########################")
        sql_host = config.get("config_sqlDB", "server")
        sql_username = config.get("config_sqlDB", "username")
        sql_password = config.get("config_sqlDB", "password")
        sql_port = int(config.get("config_sqlDB", "port"))
        sql_database = config.get("config_sqlDB", "database")
        sql_table = config.get("config_sqlDB", "table")
        from Tools.HandleSQL.HandleSQL import HandleSQL
        HandleSQL = HandleSQL(sql_host, sql_username, sql_password, sql_database, sql_port, dict_result=True)
        mail_devices = []
        for device_id in devices_id:
            running_pid = ""
            logging.info("device_id: " + device_id)
            product_name = self.get_product_info(device_id)
            logging.info(device_id + ": " + product_name)
            platform_version = self.get_device_platform_version(device_id)
            logging.info(device_id + ": " + platform_version)
            model_number = self.get_model_number(device_id)
            logging.info(device_id + ": " + model_number)
            try:
                resolution = self.get_device_resolution(device_id)
            except IndexError:
                logging.warning("solution is checked failed!")
            logging.info(device_id + ": " + resolution)
            flag_mongodb = False
            if not HandleMongoDB.query_table(deviceInfo_table_ojb, {"deviceID": device_id}):
                flag_mongodb = True
                """
                jenkins_port = max(self.get_keyword_values(
                        HandleMongoDB.query_table(deviceInfo_table_ojb, {}, {"jenkins_port": 1}), "jenkins_port")) + 1
                """
                jenkins_port = HandleMongoDB.query_table(pcInfo_table_obj, {"max_jenkins_port": {"$exists": True}}, {"max_jenkins_port": 1})[0]["max_jenkins_port"] + 1
                jenkins_port_for_pc = self.get_keyword_values(
                        HandleMongoDB.query_table(pcInfo_table_obj, {"IP": {u"$exists": True}}, {"jenkins_port": 1}), "jenkins_port")
                if jenkins_port in jenkins_port_for_pc:
                    logging.info("jenkins port is used by PC, the port above will be used!")
                    jenkins_port = max(jenkins_port_for_pc) + 1
            else:
                jenkins_port = \
                    HandleMongoDB.query_table(deviceInfo_table_ojb, {"deviceID": device_id}, {"jenkins_port": 1})[0][
                        "jenkins_port"]
            node_name = based_node_name + "_" + str(
                    jenkins_port) + "_" + product_name + "_" + platform_version + "_" + device_id
            node_name = node_name.replace(" ", "_")
            logging.info("node_name: " + node_name)
            if HandleJenkins.node_existed(node_name):
                pass
            else:
                HandleJenkins.create_node(node_name, based_node_name)
            # HandleJenkins.change_agent_port(jenkins_port)
            """
            logging.info("start to configure the port forwarding")
            logging.info("need to configure NOPASSWD:ALL for sudo")
            logging.info("sudo iptables -t nat -A PREROUTING -p tcp -m tcp --dport " + str(
                    jenkins_port) + " -j DNAT --to-destination " + ssh_jenkins_host + ":" + str(jenkins_port))
            HandleSSH.execute_command("sudo iptables -t nat -A PREROUTING -p tcp -m tcp --dport " + str(
                    jenkins_port) + " -j DNAT --to-destination " + ssh_jenkins_host + ":" + str(jenkins_port))
            logging.info(
                    "sudo iptables -t nat -A POSTROUTING -s 10.115.101.0/24 -d " + ssh_jenkins_host + " -p tcp -m tcp --dport " + str(
                            jenkins_port) + " -j SNAT --to-source " + ssh_host + ":" + str(jenkins_port))
            HandleSSH.execute_command(
                    "sudo iptables -t nat -A POSTROUTING -s 10.115.101.0/24 -d " + ssh_jenkins_host + " -p tcp -m tcp --dport " + str(
                            jenkins_port) + " -j SNAT --to-source " + ssh_host + ":" + str(jenkins_port))
            logging.info("sudo iptables -A OUTPUT -p tcp --sport " + str(jenkins_port) + " -j ACCEPT")
            HandleSSH.execute_command("sudo iptables -A OUTPUT -p tcp --sport " + str(jenkins_port) + " -j ACCEPT")
            logging.info("sudo iptables -A INPUT -p tcp --dport " + str(jenkins_port) + " -j ACCEPT")
            self.execute_cmd("sudo iptables -A INPUT -p tcp --dport " + str(jenkins_port) + " -j ACCEPT")
            logging.info("finish to configure the port forwarding")
            """
            logging.info("launch the slave")
            online_flag = False
            temporarily_offline_flag = False
            try:
                if HandleJenkins.is_node_online(node_name):
                    online_flag = True
                elif HandleJenkins.is_node_temporarily_offline(node_name):
                    temporarily_offline_flag = True
            except:
                continue # break the current loop when exception
                # temporarily_offline_flag = True
            if not online_flag:
                if not temporarily_offline_flag:
                    time_now = datetime.datetime.now().time().strftime("%H:%M:%S")
                    logging.info(
                            'schtasks /Create  /F /SC ONCE /TN ' + node_name + ' /ST ' + time_now + ' /TR "javaws ' + jenkins_server + 'computer/' + node_name + '/slave-agent.jnlp"')
                    # HandleJenkins.change_agent_port(jenkins_port)
                    self.execute_cmd(
                            'schtasks /Create  /F /SC ONCE /TN ' + node_name + ' /ST ' + time_now + ' /TR "javaws ' + jenkins_server + 'computer/' + node_name + '/slave-agent.jnlp"')
                    running_pid = self.get_running_pid(node_name, jenkins_ip)
                    if self.get_battery_level(device_id) < 30:
                        HandleJenkins.temporarily_offline_node_noConnection(node_name, message="temporarily offline node since the battery level is less than 30")
                    else:
                        online_flag = True
                        temporarily_offline_flag = False
                        # HandleJenkins.online_node(node_name)
                        self.handle_node_online(HandleJenkins, node_name, HandleMongoDB, pcInfo_table_obj, deviceInfo_table_ojb, deviceInfo_table_projectMapping_ojb)
                else:
                    if self.get_battery_level(device_id) > 85:
                        online_flag = True
                        temporarily_offline_flag = False
                        logging.info(node_name + " will be online again since battery level is over 85 or device is back and avaiable again! ")
                        try:
                            # HandleJenkins.online_node(node_name)
                            self.handle_node_online(HandleJenkins, node_name, HandleMongoDB, pcInfo_table_obj, deviceInfo_table_ojb, deviceInfo_table_projectMapping_ojb)
                            """
                            time_now = datetime.datetime.now().time().strftime("%H:%M:%S")
                            logging.info(
                                    'schtasks /Create  /F /SC ONCE /TN ' + node_name + ' /ST ' + time_now + ' /TR "javaws ' + jenkins_server + 'computer/' + node_name + '/slave-agent.jnlp"')
                            # HandleJenkins.change_agent_port(jenkins_port)
                            self.execute_cmd(
                                    'schtasks /Create  /F /SC ONCE /TN ' + node_name + ' /ST ' + time_now + ' /TR "javaws ' + jenkins_server + 'computer/' + node_name + '/slave-agent.jnlp"')
                            self.execute_cmd("schtasks /Run /TN " + node_name)
                            time.sleep(20)
                            # HandleJenkins.online_node(node_name)
                            self.handle_node_online(HandleJenkins, node_name, HandleMongoDB, pcInfo_table_obj, deviceInfo_table_ojb, deviceInfo_table_projectMapping_ojb)
                            """
                        except AssertionError:
                            pass
                    else:
                        logging.info(node_name + " still will be temporarily offline since the battery level is under 85!")
            else:
                if self.get_battery_level(device_id) < 30:
                    temporarily_offline_flag = True
                    online_flag = False
                    HandleJenkins.offline_node(node_name, message="temporarily offline node since the battery level is less than 30")
                    logging.info(node_name + " will be temporarily offline since the battery level is less than 30!")
                else:
                    logging.info(node_name + " is online!")
            logging.info("start to handle the device info in database!")
            device_info = {}
            device_info["deviceID"] = device_id
            device_info["productName"] = product_name
            device_info["platformVersion"] = platform_version
            device_info["jenkins_port"] = jenkins_port
            device_info["nodeName"] = node_name
            device_info["model_number"] = model_number
            print running_pid
            if running_pid != "":
                device_info["running_pid"] = running_pid
            else:
                device_info_from_table = HandleMongoDB.query_table(deviceInfo_table_ojb, {"deviceID": node_name.split("_")[-1]})[0]
                if "running_pid" in device_info_from_table.keys():
                    device_info["running_pid"] = device_info_from_table["running_pid"]
            if temporarily_offline_flag:
                device_info["status"] = "charging"
            else:
                device_info["status"] = "free"
            if flag_mongodb:
                mail_devices.append(node_name)
                HandleMongoDB.insert_item(deviceInfo_table_ojb, device_info)
            else:
                HandleMongoDB.update_item(deviceInfo_table_ojb, condition={"deviceID": device_id}, data=device_info)
            if HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": device_id}):
                logging.info("start to handle the device under project testing!")
                project_name = \
                    HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": device_id})[0][
                        "project"]
                if project_name == "compatibility":
                    model = device_info["productName"]
                    model_result_from_sql = HandleSQL.query_sql('SELECT model FROM devices WHERE model LIKE "' + model + '%"', return_result=True)
                    if model_result_from_sql:
                        model_result_from_sql = list(map(lambda x: x["model"], model_result_from_sql))
                        for i in range(1, 100):
                            if model + "_" + str(i) not in model_result_from_sql:
                                model = model + "_" + str(i)
                                break

                    if HandleSQL.query_sql('select * from ' + sql_table + ' where device_no="' + device_id + '";',
                                           return_result=True):
                        if HandleSQL.query_sql(
                                                                'select nodeName from ' + sql_table + ' where device_no="' + device_id + '";',
                                return_result=True)[0]["nodeName"] != node_name:
                            HandleSQL.query_sql('update ' + sql_table + ' set system_version="V' + device_info[
                                "platformVersion"] + '", sys_platform="' +
                                                device_info["platformVersion"][
                                                :len(device_info["platformVersion"]) - len(
                                                        device_info["platformVersion"].split(".")[
                                                            -1]) - 1] + '", nodeName="' + node_name + '", use_status="' + device_info["status"] + '", model_number="' + device_info["model_number"]  + '" where device_no="' + device_id + '";')
                    else:
                        table_id = max(map(lambda x: int(x["id"]),
                                           HandleSQL.query_sql("select id from " + sql_table + ";", return_result=True))) + 1
                        HandleSQL.query_sql(
                                "insert into " + sql_table + ' (id, imei, system_version, model, device_no, use_status, resolution, product_line, sys_platform, nodeName)' + " values (" + str(table_id) + ', "", "' +
                                device_info["platformVersion"] + '", "' + model + '", "' + device_id + '", "' + device_info["status"] + '", "' + resolution + '", "", "' + device_info[
                                                                                                   "platformVersion"][
                                                                                               :len(
                                                                                                       device_info[
                                                                                                           "platformVersion"]) - len(
                                                                                                       device_info[
                                                                                                           "platformVersion"].split(
                                                                                                           ".")[
                                                                                                           -1]) - 1] + '", "' + node_name + '");')
            # 20160711 Add the max port record.
            max_jenkins_port_pcInfo = HandleMongoDB.query_table(pcInfo_table_obj, {"max_jenkins_port": {"$exists": True}}, {"max_jenkins_port": 1})[0]["max_jenkins_port"]
            if jenkins_port > max_jenkins_port_pcInfo:
                logging.info("need to update the max jenkins port to db!")
                HandleMongoDB.update_item(pcInfo_table_obj, {"max_jenkins_port": max_jenkins_port_pcInfo}, {"max_jenkins_port": jenkins_port})

        logging.info("###############start to handle the invalid Device####################")
        nodeNames_from_db = map(lambda x: x["nodeName"], HandleMongoDB.query_table(deviceInfo_table_ojb, {}, {"nodeName": 1}))
        need_to_removed_nodeNames = filter(lambda x: x.split("_")[-1] not in devices_id and re.match(based_node_name + "_", x), nodeNames_from_db)
        nedd_to_removed_nodeNames_from_Jenkins = filter(lambda x: x not in nodeNames_from_db, filter(lambda x: re.match(based_node_name + "_", x), HandleJenkins.get_all_nodes()))
        need_to_removed_nodeNames += nedd_to_removed_nodeNames_from_Jenkins
        need_to_removed_nodeNames = list(set(need_to_removed_nodeNames))
        if need_to_removed_nodeNames:
            for need_to_removed_nodeName in need_to_removed_nodeNames:
                operation_flag = True
                if need_to_removed_nodeName in nedd_to_removed_nodeNames_from_Jenkins:
                    operation_flag = False
                if not HandleJenkins.has_query_items(need_to_removed_nodeName):
                    # if operation_flag:
                        # need_to_removed_port = map(lambda x: x["jenkins_port"], HandleMongoDB.query_table(deviceInfo_table_ojb, {"nodeName": need_to_removed_nodeName}, {"jenkins_port": 1}))[0]
                    # else:
                        # need_to_removed_port = need_to_removed_nodeName.replace(based_node_name, "").split("_")[0]
                    # 20160630 add process killed method
                    """
                    try:
                        self.kill_process(re.findall(".*//(\d+\.\d+\.\d+\.\d+)", jenkins_server)[0] + ":" + str(need_to_removed_port))
                    except IndexError:
                        logging.info("process is not found!")
                    """
                    HandleJenkins.remove_node(need_to_removed_nodeName)
                    device_info_from_table = HandleMongoDB.query_table(deviceInfo_table_ojb, {"deviceID": need_to_removed_nodeName.split("_")[-1]})[0]
                    print device_info_from_table
                    if "running_pid" in device_info_from_table.keys():
                        need_to_kill_pid = device_info_from_table["running_pid"]
                        self.execute_cmd("taskkill /F /PID " + need_to_kill_pid)
                        logging.info(need_to_kill_pid + "is killed since the device is not avaiable now!")
                    logging.info(need_to_removed_nodeName + " is removed! ")
                    #if not HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": need_to_removed_nodeName.split("_")[-1], "project": {"$in": ["security", "monkey"]}}):
                    # HandleMongoDB.delete_items(deviceInfo_table_ojb, {"nodeName": need_to_removed_nodeName})
                if HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": need_to_removed_nodeName.split("_")[-1], "project": "compatibility"}):
                        # HandleMongoDB.delete_items(deviceInfo_table_projectMapping_ojb, {"deviceID": need_to_removed_nodeName.split("_")[-1]})
                        HandleSQL.query_sql("update " + sql_table + ' set deleted=1 where nodeName="' + need_to_removed_nodeName + '";')
                        HandleSQL.query_sql("update " + sql_table + ' set use_status="' + 'offline"' + ' where nodeName="' + need_to_removed_nodeName + '";')

        need_to_change_deleted_status_False_nodeNames = filter(lambda x: x.split("_")[-1] in devices_id and re.match(based_node_name, x), map(lambda x: x["nodeName"], HandleMongoDB.query_table(deviceInfo_table_ojb, {}, {"nodeName": 1})))
        for need_to_change_deleted_status_False_nodeName in need_to_change_deleted_status_False_nodeNames:
            if HandleMongoDB.query_table(deviceInfo_table_projectMapping_ojb, {"deviceID": need_to_change_deleted_status_False_nodeName.split("_")[-1], "project": "compatibility"}):
                HandleSQL.query_sql("update " + sql_table + ' set deleted=0 where nodeName="' + need_to_change_deleted_status_False_nodeName + '";')
                HandleSQL.query_sql("update " + sql_table + ' set use_status="' + 'free"' + ' where nodeName="' + need_to_change_deleted_status_False_nodeName + '";')
                logging.info(need_to_change_deleted_status_False_nodeName + " is set False for deleted! ")
        HandleMongoDB.close_mongodb()
        # HandleSSH.close_client_connection()
        HandleSQL.commit_change()
        HandleSQL.close()
        if os.path.isfile("params.txt"):
            os.remove("params.txt")
        if mail_devices:
            logging.info("#######need to send email###########")
            File = open("params.txt", "w")
            File.write("mail_content=" + "\n")
            File.write("mail_list=" + "xiaobo.chi@tcl.com,wei.y@tcl.com,cc:zhanyu.huo@tcl.com,leisun@tcl.com" + "\n")
            File.write("mail_subject=" + str(mail_devices) + " are new added, please check!")
            File.close()
        self.close_invalid_connection(jenkins_ip)
        logging.info("#########################end##############################")


if __name__ == "__main__":
    HandleDevice = HandleDevice()
    HandleDevice.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import logging
import urllib
import subprocess
import re
import datetime
import time
import Queue
import threading

logging.basicConfig(level=logging.INFO)


class Execommand(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
            out, err = self.process.communicate()
            print 'Thread finished'
            return out

        que = Queue.Queue()
        thread = threading.Thread(target=que.put(target()))
        thread.start()

        thread.join(timeout)
        result = que.get_nowait()
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        # print self.process.returncode
        if not result:
            return None
        return result.split("\r\n")

class Monkey(object):
    def __init__(self, download_url, time_count):
        self.download_url = download_url
        logging.info("========start to test!=========")
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # self.tn = Telnet()
        self.download_status, self.apk_path = self.download_apk()
        self.apk_info = self.get_apk_info()
        self.package_name = re.findall("package: name='(.*?')", self.apk_info)[0].replace("'", "")
        self.time_count = str(time_count)
        logging.info('package name:' + self.package_name)
        logging.info('time_count:' + self.time_count)
        self.logs_home = os.path.join(os.path.dirname(__file__), "logs" + "\\" + self.download_url.split("/")[-1].split(".")[0] + "\\" + self.current_time + "\\")
        self.devices = self.get_devices()

    def download_apk(self):
        dir_name = os.path.dirname(__file__)
        apk_down_path = os.path.join(dir_name, self.download_url.split("/")[-1].split(".")[0] + '_' + self.current_time + '.apk')
        print apk_down_path
        if os.path.isfile(apk_down_path):
            os.remove(apk_down_path)
        logging.info('apk path:' + apk_down_path)
        logging.info('start to get apk from ' + self.download_url)
        urllib.urlretrieve(self.download_url, apk_down_path)
        if "ThemeStore.apk" in self.download_url:
            apk_down_path = os.path.join(dir_name, "ThemeDemo.apk")
            urllib.urlretrieve(self.download_url.replace("ThemeStore.apk", "ThemeDemo.apk"), apk_down_path)
        if os.path.isfile(apk_down_path):
            status = 0
        else:
            status = 1
        return status, apk_down_path

    def install_apk(self, device_id):
        logging.info('========install apk=========')
        try:
            command = "adb -s " + device_id + " install -r " + self.apk_path
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            if len(filter(lambda x: "Success" in x, output)) == 0:
                logging.info('install apk fail!')
                # 2016/11/09 add reboot
                self.execute_cmd("adb -s " + device_id + " reboot")
                time.sleep(120)
                # sys.exit(0)
                os._exit(1)

            logging.info('========install wifi apk=========')
            #     for device_id in devices_id:
            command = "adb -s " + device_id + " install -r WIFIdaemon-xili.apk && " + \
                      "adb -s " + device_id + " shell am startservice --user 0 -n com.mie.wifidaemon/.WiFiService"
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            logging.info('========install input method of appium=========')
            #     for device_id in devices_id:
            command = "adb -s " + device_id + " install -r UnicodeIME-debug.apk"
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            # time.sleep(5)
            logging.info('========set appium as the default input method=========')
            #     for device_id in devices_id:
            command = "adb -s " + device_id + " shell settings put secure default_input_method io.appium.android.ime/.UnicodeIME"
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            logging.info('========install ClearNotification.apk=========')
            #     for device_id in devices_id:
            command = "adb -s " + device_id + " install -r ClearNotification.apk"
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            logging.info('========Launch ClearNotification.apk=========')
            #     for device_id in devices_id:
            command = "adb -s " + device_id + " shell am start -W apptest.szc.servicetest/apptest.szc.servicetest.MainActivity"
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            if "SingleLogin.apk" in self.download_url:
                logging.info('========install AccountSDKDemo for singleLogin =========')
                #     for device_id in devices_id:
                command = "adb -s " + device_id + " install -r AccountSDKDemo.apk"
                logging.info(command)
                output = self.execute_cmd(command)
                logging.info(output)
            if "ThemeStore.apk" in self.download_url:
                logging.info('========install ThemeDemo for ThemeStore =========')
                #     for device_id in devices_id:
                command = "adb -s " + device_id + " install -r " + self.apk_path.replace(self.apk_path.split(os.sep)[-1], "ThemeDemo.apk")
                logging.info(command)
                output = self.execute_cmd(command)
                logging.info(output)

        except AssertionError:
            logging.info('apk install timeout')
            os._exit(0)

    def uninstall_apk(self, device_id):
        logging.info('========install apk=========')
        try:
            command = "adb -s " + device_id + " uninstall " + self.package_name
            logging.info(command)
            output = self.execute_cmd(command)
            logging.info(output)
            if len(filter(lambda x: "Success" in x, output)) == 0:
                logging.error('uninstall apk fail!')
                # sys.exit(0)
                # os._exit(0)

        except AssertionError:
            logging.info('apk install timeout')
            os._exit(0)

    def run_monkey(self, device_id):
        logging.info('=========run monkey=======')
        logs_dir = self.logs_home + 'pc_logs' + "\\"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # for device_id in devices_id:
        seed = random.randint(0, 1000)
        logging.info('seed : ' + str(seed))
        if self.package_name == 'com.tcl.live.avg':
            self.package_name = 'com.tcl.live'
        if self.package_name == "com.tcl.sso.accountservice":
            self.package_name = "com.tcl.account.sdk.example"
        command = "adb -s " + device_id \
                  + " shell monkey " + "-p " + self.package_name + " -s " + str(seed) + " --throttle 800 " \
                  + "--ignore-crashes --ignore-timeouts --ignore-security-exceptions --monitor-native-crashes --ignore-native-crashes -v -v -v " \
                  + self.time_count + " > " + logs_dir + device_id + ".txt"
        logging.info(command)
        self.execute_cmd(command, timeout=60*60*3)
        # logging.info(output)

    def execute_cmd(self, cmd, timeout=120):
        """
        执行cmd命令
        :param cmd: 需要执行cmd命令
        :return: 返回执行结果
        """
        Command = Execommand(cmd)
        return Command.run(timeout)

    def get_devices(self):
        """
        devices = map(lambda x: x.replace("\tdevice\r\n", ""),
                      filter(lambda x: re.search(".*\tdevice\r\n", x), self.execute_cmd("adb devices")))
        if len(devices) == 0:
            self.execute_cmd("adb kill-server&adb start-server")
            devices = map(lambda x: x.replace("\tdevice\r\n", ""),
                          filter(lambda x: re.search(".*\tdevice\r\n", x), self.execute_cmd("adb devices")))
        if len(devices) == 0:
            logging.info('no device was found')
            sys.exit(1)
        else:
            logging.info("devices info: " + str(devices))
        """
        print [self.GetJenkinsVar("nodeName").split("_")[-1]]
        return [self.GetJenkinsVar("nodeName").split("_")[-1]]

    def get_apk_info(self):
        # output = self.tn.telnet_only_execute_command('aapt d badging "' + self.apk_path + '"', 5, ">")
        output = self.execute_cmd('aapt d badging "' + self.apk_path + '"')
        return output[0]

    def main(self):
        if self.download_status == 0:
            for device_id in self.devices:
                self.install_apk(device_id)
                self.run_monkey(device_id)
                self.uninstall_apk(device_id)
                # 冗余100s
                # time.sleep(0.2 * int(time_count) + 100)
        else:
            logging.info('download apk is fail !!!')
            sys.exit(1)
        logging.info("========test finish!=========")

    def GetJenkinsVar(self, key):
        try:
            value = os.environ.get(key)
        except Exception:
            value = os.environ.get(key.upper())
        #print('value = ',value)
        if(not value):
            value = ''
        #print( os.path.join(r'c:/a',value) )
        return value

if __name__ == "__main__":
    download_url = "http://10.115.101.230:8080/jenkins/view/beautifulStorey/job/beautifulStorey_Monkey/lastSuccessfulBuild/artifact/beautifulStorey.apk"
    Monkey = Monkey(download_url, 200)
    Monkey.main()

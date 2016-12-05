# -*- coding: utf-8 -*-
import time
import sys

__author__ = 'wei.y'
import subprocess


def exe_cmd(cmd, shell=False, timeout=600, stdout_type=subprocess.SW_HIDE):
    p = subprocess.Popen(cmd, shell=shell, stdout=stdout_type, stderr=subprocess.STDOUT)
    times = 0
    while True:
        if p.poll() is not None:
            break
        if timeout <= times:
            p.terminate()
            print u'执行超时退出'
            break
        times += 1
        time.sleep(1)
    # retval = p.wait()
    # print retval
    if subprocess.PIPE == stdout_type:
        return p.stdout.readlines()
        # list_result_info = []
        # for line in p.stdout.readlines():
        #     list_result_info.append(line)
        #     print line
        # return list_result_info
    return []


def get_uid(package_name):
    cmd = 'adb shell "ps |grep %s "' % package_name
    ps_infos = exe_cmd(cmd, stdout_type=subprocess.PIPE)
    pid = ''
    if ps_infos:
        for ps_info in ps_infos:
            pid_infos = ps_info.replace('\r\r\n', '').split(' ')
            if pid_infos[-1] == package_name:
                for pid_info in pid_infos:
                    if pid_info == '':
                        pid_infos.remove(pid_info)
                pid = pid_infos[1]
                break
    if pid:
        cmd = 'adb shell "cat /proc/%s/status |grep Uid' % pid
        cat_uid_infos = exe_cmd(cmd, stdout_type=subprocess.PIPE)
        if cat_uid_infos:
            uid_infos = cat_uid_infos[0].replace('\r\r\n', '').split('\t')
            return uid_infos[1]
    return ''


def get_cpu_mem_infos(file_path):
    """
        解析top命令统计结果，返回应用性能统计信息
    :param file_path:
    :return:
    """
    result_info = {}
    with open(file_path) as f:
        lines = f.readlines()
        pid = ''
        package_name = ''
        app_uid = ''
        cpu_results = ["cpu(%)"]
        VSS_list = ['VSS(K)']
        RSS_list = ['RSS(K)']
        Num_list = ['nums']
        num = 1
        for line in lines:
            results = []
            if line:
                strs = line.split(' ')
                for stri in strs:
                    if stri:
                        results.append(stri)
                if not pid:
                    pid = results[0]
                    package_name = results[9]
                    app_uid = results[8]
                cpu_results.append(float(results[2].replace('%', '')))
                VSS_list.append(float(results[5].replace('K', '')))
                RSS_list.append(float(results[6].replace('K', '')))
                Num_list.append(num)
                num += 1
        result_info["nums"] = Num_list
        result_info["pid"] = pid
        result_info["cpu(%)"] = cpu_results
        result_info["VSS(K)"] = VSS_list
        result_info["RSS(K)"] = RSS_list
        result_info["uid"] = app_uid
        result_info["packageName"] = package_name.replace('\r\n', '')
    return result_info



if __name__ == '__main__':
#     # cmd = 'adb shell monkey --monitor-native-crashes -p com.tcl.usercare --throttle 300 -v -v 200'
#     # exe_cmd(cmd)
#     get_cpu_mem_infos(r'D:/autoTest/PerformanceInfo/result.txt')
    uid = get_uid('com.tcl.usercare')
    for i in xrange(10):
        cmd = 'adb shell cat /proc/uid_stat/%s/tcp_rcv' % uid
        print exe_cmd(cmd, stdout_type=subprocess.PIPE)
    # cmd = 'adb shell "ps |grep com.tcl.usercare'
    # print exe_cmd(cmd, stdout_type=subprocess.PIPE)
    # cmd = 'adb shell "cat /proc/26813/status |grep Uid'
    # print exe_cmd(cmd, stdout_type=subprocess.PIPE)
#     asdasd()
#
#     # exe_cmd('adb install -r E:\\test\\tclmarket-v4.3.2-201511021646-product.apk')
#     # exe_cmd('adb shell ping -c 5 172.26.50.50')

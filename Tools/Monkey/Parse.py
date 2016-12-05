#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2015年3月6日

@author: yangfan
"""
import os
import sys
import re
import shutil
import time
import logging
import TJIRA
import DB
import ConfigParser


logging.basicConfig(level=logging.INFO)


def parse_log():
    logging.info('======parse log=====')
    logs_path = []
    for root, dirs, files in os.walk(Monkey.logs_home + 'pc_logs/'):
        for File in files:
            logs_path.append(os.path.join(root, File))

    # 拷贝手机里的log并删除手机里对应的文件夹
    phone_logs_path = []
    for i in devices_info:
        phone_logs_dir = Monkey.logs_home + 'phone_logs/' + i
        if not os.path.exists(phone_logs_dir):
            os.makedirs(phone_logs_dir)
        comm = "adb -s " + i + " pull " + log_dir[Monkey.package_name] + ' ' + phone_logs_dir
        print log_dir[Monkey.package_name]
        print type(log_dir[Monkey.package_name])
        logging.info(comm)
        """
        Monkey.tn.telnet_only_execute_command(comm, 60, ">")
        Monkey.tn.telnet("adb shell", "adb -s " + i + " shell", "shell@", 20, "adb not connect devices!", "$ ")
        Monkey.tn.telnet("rm -r", "rm -r " + log_dir[Monkey.package_name], "shell@", 5,
                         "remove log files from phone is failed!", "$ ")
        Monkey.tn.telnet("exit", "exit", ">", 5, "exit to telnet main page is failed!", ">")
        """
        logging.info(str((Monkey.execute_cmd(comm))))
        logging.info(str(Monkey.execute_cmd("adb -s " + i + " shell " + "rm -r " + log_dir[Monkey.package_name])))
        for root, dirs, files in os.walk(phone_logs_dir):
            for file in files:
                phone_logs_path.append(os.path.join(root, file))

    device_count = []
    device_monkey_parse_log = {}
    crash_name = set()
    device_crash_name_to_id = {}
    device_crash_id_to_name = {}
    index = 0
    # 处理PC上的log 
    for path in logs_path:
        device_id_pc = os.path.basename(path).split(".")[0]
        # 过滤不存在的设备产生的log
        if device_id_pc in Monkey.devices:
            _f = open(path)
            try:
                monkey_log = _f.read()
                monkey_parse_log = re.findall(r'// CRASH:([\s\S]*?)(?:// \r\n|\r\n\r\nS|\r\n\r\n:)', monkey_log)
                #             monkey_parse_log = re.findall(r'// CRASH:([\s\S]*?)// \r\n', monkey_log)
                parse_count = len(monkey_parse_log)
                count = len(re.findall(r'// CRASH', monkey_log))

                print '********************'
                print parse_count
                print count
                print '********************'
                #             assert parse_count == count, "count is error !!!"
                for i in monkey_parse_log:
                    crash_type, crash = get_crash_type_from_pc(i)
                    crash_name.add(crash_type)
            finally:
                _f.close()
            _device_id = device_id_pc
            device_count.append(_device_id)
            device_monkey_parse_log[_device_id] = monkey_parse_log

    # 处理手机上的log
    for phone_log_path in phone_logs_path:
        device_id_phone = os.path.basename(phone_log_path).split(".")[0]
        if device_id_phone in Monkey.devices:
            if '.txt' in phone_log_path or '.log' in phone_log_path:
                _f = open(phone_log_path)
                try:
                    phone_log = _f.read()
                    crash_type, crash_name_short = get_crash_type_from_phone(phone_log)
                    crash_name.add(crash_type)
                finally:
                    _f.close()

    for i in crash_name:
        print i
        index += 1
        device_crash_name_to_id[i] = index
        device_crash_id_to_name[index] = i

    rename_phone_log(phone_logs_path, device_crash_name_to_id)

    for device in device_count:
        parse_log_path_home = Monkey.logs_home + 'pc_parse/'
        if not os.path.exists(parse_log_path_home):
            os.makedirs(parse_log_path_home)
        for device_log in device_monkey_parse_log[device]:
            if Monkey.package_name in device_log:
                parse_logs_path = []
                _temp = []
                for root, dirs, files in os.walk(parse_log_path_home):
                    for File in files:
                        parse_logs_path.append(os.path.join(root, File))

                crash_type, crash_name_short = get_crash_type_from_pc(device_log)
                crash_id = get_crash_id(crash_type, device_crash_name_to_id)

                log_name = parse_log_path_home + Monkey.download_url.split("/")[-1].split(".")[0] + '_' \
                           + crash_name_short + '_' + 'TYPE_' + crash_id + '_' \
                           + get_product_name(device) + '_'
                if not parse_logs_path:
                    index = str(1)
                else:
                    for name in parse_logs_path:
                        if log_name in name:
                            _temp.append(name[name.rindex('_') + 1:name.rindex('.')])
                    if not _temp:
                        index = str(1)
                    else:
                        _temp.sort(key=int, reverse=True)
                        index = str(int(_temp[0]) + 1)
                _parse_log = open(log_name + index + '.txt', 'w')
                try:
                    _parse_log.writelines('===================================================\r\n')
                    _parse_log.writelines(Monkey.apk_info + "\r\n")
                    _parse_log.writelines('\r\n===================================================\r\n')
                    _device_info = devices_info[device]
                    _parse_log.writelines('\r\n'.join(_device_info))
                    _parse_log.writelines('\r\n===================================================\r\n')
                    _parse_log.writelines(device_log)
                finally:
                    _parse_log.close()
            else:
                print('--------start---非本进程产生的log---------')
                print(device_log)
                print('--------end---非本进程产生的log---------')
    push_log_count_info(device_crash_id_to_name)
    package_version = open(Monkey.logs_home + 'apk_version.txt', 'w')
    try:
        # ver = Monkey.apk_info[2]
        package_version.writelines(re.findall("versionName='(.*?')", Monkey.apk_info)[0].replace("'", ""))
    finally:
        package_version.close()


def rename_phone_log(phone_logs_path, device_crash_name_to_id):
    parse_log_path_home = Monkey.logs_home + 'phone_parse/'
    if not os.path.exists(parse_log_path_home):
        os.makedirs(parse_log_path_home)
    for phone_log_path in phone_logs_path:
        if '.txt' in phone_log_path or '.log' in phone_log_path:
            _f = open(phone_log_path)
            try:
                phone_log = _f.read()
                crash_type, crash_name_short = get_crash_type_from_phone(phone_log)
                crash_id = get_crash_id(crash_type, device_crash_name_to_id)
            finally:
                _f.close()
            device = os.path.dirname(phone_log_path)
            parse_logs_path = []
            _temp = []
            for root, dirs, files in os.walk(parse_log_path_home):
                for _file in files:
                    parse_logs_path.append(os.path.join(root, _file))
            print('---------------parse_logs_path------------------------')
            print(parse_logs_path)
            print(device)
            log_name = parse_log_path_home + Monkey.download_url.split("/")[-1].split(".")[0] + '_' \
                       + crash_name_short + '_' + 'TYPE_' + crash_id + '_' \
                       + get_product_name(device) + '_'

            if not parse_logs_path:
                # if not parse_logs_path:
                index = str(1)
            else:
                for name in parse_logs_path:
                    if log_name in name:
                        _temp.append(name[name.rindex('_') + 1:name.rindex('.')])
                if not _temp:
                    index = str(1)
                else:
                    _temp.sort(key=int, reverse=True)
                    index = str(int(_temp[0]) + 1)
            if len(phone_log) != 0:
                _parse_log = open(log_name + index + '.txt', 'w')
                try:
                    _parse_log.write(phone_log)
                finally:
                    _parse_log.close()
        else:
            # 如果不是txt文件，那么就是dump文件，原样拷贝到解析目录
            shutil.copy(phone_log_path, parse_log_path_home)


def push_log_count_info(device_crash_id_to_name):
    logs_path = []
    logs_pc_path = []
    logs_phone_path = []
    for root, dirs, files in os.walk(Monkey.logs_home + 'pc_parse/'):
        for _file in files:
            logs_path.append(_file)
            _file = _file[find_str(_file, '_', 3) + 1:find_str(_file, '_', 4)]
            logs_pc_path.append(_file)

    for root, dirs, files in os.walk(Monkey.logs_home + 'phone_parse/'):
        for _file in files:
            if '.txt' in _file or '.log' in _file:
                logs_path.append(_file)
                _file = _file[find_str(_file, '_', 3) + 1:find_str(_file, '_', 4)]
                logs_phone_path.append(_file)
    type_and_id_set = set()
    type_and_id_list = []
    type_and_id_product_set = set()

    for log_path in logs_path:
        type_and_id = log_path[find_str(log_path, '_', 1) + 1:find_str(log_path, '_', 4)]
        type_and_id_set.add(type_and_id)
        type_and_id_list.append(type_and_id)
        type_and_id_product = log_path[find_str(log_path, '_', 1) + 1:log_path.rindex('_')]
        type_and_id_product_set.add(type_and_id_product)

    _f = open(Monkey.logs_home + 'count.txt', 'w')
    try:
        for ti in type_and_id_set:
            type_id = ti[ti.rindex('_') + 1:]
            type_name = ti[:ti.index('_')]
            count = type_and_id_list.count(ti)
            try:
                exce = find_str(device_crash_id_to_name[int(type_id)], ' ', 1)
            except:
                exce = -1
            if exce == -1:
                argument = 'none'
            else:
                argument = device_crash_id_to_name[int(type_id)][exce:]
                argument = argument.replace('\r\n', '').replace('\t', '').replace('"', '')
            # .replace(' ', '')

            product = ''
            for pr in type_and_id_product_set:
                if ti in pr:
                    product += pr[find_str(pr, '_', 3) + 1:] + ' '

            # 判断来源
            pc = 'false'
            phone = 'false'
            if type_id in logs_pc_path:
                pc = 'true'
            if type_id in logs_phone_path:
                phone = 'true'

            if pc == 'false' and phone == 'true':
                origin = 'AppLog'
            elif pc == 'true' and phone == 'false':
                origin = 'MonkeyLog'
            elif pc == 'true' and phone == 'true':
                origin = 'App&MonkeyLog'
            else:
                origin = ''

            _f.writelines(
                    origin + '|' + type_name + '|' + type_id + '|' + argument + '|' + str(
                            count) + '|' + product + '\r\n')
    finally:
        _f.close()


def txt_to_html():
    logging.info('txt_to_html')
    _f = open(Monkey.logs_home + 'index.html', 'w')
    r = open(Monkey.logs_home + 'count.txt')
    try:
        _f.write('''
        <table width="300" border="1" cellpadding="0" cellspacing="0" bordercolor="#B03060" style="border-collapse:collapse;">
        <tr>
            <td style="text-align:center">ID</td>
            <td style="text-align:center">FROM</td>
            <td style="text-align:center">TYPE</td>
            <td style="text-align:center">TYPE_ID</td>
            <td style="text-align:center">DETAILS</td>
            <td style="text-align:center">CRASH COUNT</td>
            <td style="text-align:center">DEVICES</td> 
        <tr> 
        ''')
        index = 0
        for _info in r.read().strip().split('\r\n'):
            index += 1
            if _info == '':
                _f.writelines('<tr> \r\n')
                _f.writelines('<td style="text-align:center">' + str(index) + '''</td>
                <td style="text-align:center">none</td>
                <td style="text-align:center">none</td>
                <td style="text-align:center">none</td>
                <td style="text-align:center">none</td>
                <td style="text-align:center">none</td>
                <td style="text-align:center">none</td>''')
                _f.writelines('</tr> \r\n')
            else:
                create_table(_f, _info, str(index))
        _f.write('''
            </table>
        ''')
    finally:
        _f.close()


def create_table(_f, i, index):
    _info = i.split('|')
    _f.writelines('<tr> \r\n')
    _f.writelines('<td style="text-align:center">' + index + '</td><td style="text-align:center">' + _info[0] +
                  '</td><td style="text-align:center">' + _info[1] + '</td><td style="text-align:center">' + _info[2] +
                  '</td><td style="text-align:left">' + _info[3] + '</td><td style="text-align:center">' + _info[4] +
                  '</td><td style="text-align:center">' + _info[5] + '</td>')
    _f.writelines('</tr> \r\n')


def is_dir_null(_path):
    empty = False
    if os.path.exists(_path):
        for root, dirs, files in os.walk(_path):
            if len(files) == 0:
                empty = True
    return empty


# 第3个参数为第几次出现
def find_str(string, sub_str, find_cnt):
    list_str = string.split(sub_str, find_cnt)
    if len(list_str) <= find_cnt:
        return -1
    return len(string) - len(list_str[-1]) - len(sub_str)


def get_crash_type_from_pc(device_log):
    crash = re.findall(r'// Long Msg: ([\s\S]*?)\r\n', device_log)

    device_log = device_log[find_str(device_log, 'Build Time', 1):]
    start = find_str(device_log, '//', 1) + 3
    end = find_str(device_log, '//', 3)
    crash_type = device_log[start:end]
    crash_type = crash_type.replace('\r\n', '//').replace('// \t', '')
    crash = crash_type[:crash_type.find('//')]
    if crash.find(':') == -1:
        crash_name = crash[:]
    else:
        crash_name = crash[:crash.find(':')]
    return crash_type, crash_name


def get_crash_id(crash_type, device_crash_id=None):
    if not device_crash_id:
        device_crash_id = {}
    return str(device_crash_id[crash_type])


def get_crash_type_from_phone(phone_log):
    phone_log = phone_log[find_str(phone_log, 'the crashed thread', 1):]
    crash_type = phone_log[find_str(phone_log, '\n', 1) + 1:find_str(phone_log, 'at ', 2)]
    crash_type = crash_type.replace('\n\t', '//')
    crash = crash_type[:crash_type.find('//')]
    if crash.find(':') == -1:
        crash_name = crash[:]
    else:
        crash_name = crash[:crash.find(':')]

    return crash_type, crash_name


def get_product_name(device):
    _device_info = devices_info[device]
    # 遍历device_info,取出ro.product.name
    for de in _device_info:
        if 'ro.product.name' in de:
            device_name = de[de.find(':') + 1:]
            return device_name
    return 'none'


def get_device_info(_devices_id=None):
    print('---------get_device_info---------------')
    if not _devices_id:
        _devices_id = []
    devices_info = {}
    for device_id in _devices_id:
        command_output = Monkey.execute_cmd('adb -s ' + device_id + ' shell getprop | find "product"')
        command_output = map(lambda x: x.replace("[", "").replace("]", "").replace(" ", "").strip(), command_output)
        # print command_output
        devices_info[device_id] = command_output
    return devices_info


def get_description(result, type_id):
    print '---------result----------'
    logs_path = []
    log_from = result[:find_str(result, '|', 1)]
    _type = 'TYPE_' + type_id
    log_path = ''
    if log_from == 'AppLog' or log_from == 'App&MonkeyLog':
        for root, dirs, files in os.walk(Monkey.logs_home + 'phone_parse/'):
            for _file in files:
                logs_path.append(os.path.join(root, _file))
    elif log_from == 'MonkeyLog':
        for root, dirs, files in os.walk(Monkey.logs_home + 'pc_parse/'):
            for _file in files:
                logs_path.append(os.path.join(root, _file))
    for i in logs_path:
        if _type in i:
            log_path = i
            break
    return open(log_path).read()


def compare_version(version1, version2):
    version1 = version1.replace('V', '').replace('v', '').replace('D', '').replace('d', '')
    version2 = version2.replace('V', '').replace('v', '').replace('D', '').replace('d', '')

    if "_" in version1:
        version_array1 = filter(lambda x: re.search("\d+\.", x), version1.split("_"))[0].split('.')
    elif "-" in version1:
        version_array1 = filter(lambda x: re.search("\d+\.", x), version1.split("-"))[0].split('.')
    else:
        version_array1 = version1.split('.')
    if "_" in version1:
        version_array2 = filter(lambda x: re.search("\d+\.", x), version2.split("_"))[0].split('.')
    elif "-" in version1:
        version_array2 = filter(lambda x: re.search("\d+\.", x), version2.split("-"))[0].split('.')
    else:
        version_array2 = version2.split('.')
    idx = 0

    if len(version_array1) <= len(version_array2):
        min_length = len(version_array1)
    else:
        min_length = len(version_array2)

    # diff = 0

    while idx < min_length and (int(version_array1[idx]) - int(version_array2[idx]) == 0):
        #             and (diff = version_array1[idx].compareTo(version_array2[idx])) == 0) {//再比较字符
        #        if(idx != min_length - 1):
        idx += 1
    # 如果已经分出大小，则直接返回，如果未分出大小，则再比较位数，有子版本的为大；
    #    diff = int(version_array1[idx]) - int(version_array2[idx])
    if idx == min_length:
        idx -= 1
    print int(version_array1[idx])
    print int(version_array2[idx])
    return int(version_array1[idx]) - int(version_array2[idx])


def compare_time(update_time, _current_time):
    _date = _current_time[:_current_time.find('_')]
    print _date
    _time = _current_time[_current_time.find('_') + 1:]
    print _time
    _time = _time.replace('-', ':')
    _current_time = _date + ' ' + _time
    print _current_time
    print update_time
    current = time.mktime(time.strptime(_current_time, '%Y-%m-%d %H:%M:%S'))
    update = time.mktime(time.strptime(update_time, '%Y-%m-%d %H:%M:%S'))
    if current - update >= 60 * 60 * 24 * 7:
        return True
    else:
        return False


def close_bug():
    print '============close bug==========='
    print components_name[Monkey.package_name]
    for i in jira.query_issue(components_name[Monkey.package_name], 'Solved'):
        logging.info('jira.query_issue:' + i)
        query_result_by_key = jira.query_issue_bykey((i,))
        print query_result_by_key
        old_ver = query_result_by_key[i][2].replace('\n', '')
        new_ver = apk_version.replace('\n', '')
        logging.info('old_ver:' + old_ver)
        logging.info('new_ver:' + new_ver)
        update_time = query_result_by_key[i][1]

        if compare_version(old_ver, new_ver) < 0 and compare_time(update_time, current_time):
            print '关闭bug'
            close_comment = u'=================================================================================\r\n' + \
                            u'【项目名称】：' + Monkey.download_url.split("/")[-1].split(".")[0] + '\r\n' + \
                            u'【当前版本】：' + apk_version + '\r\n' + \
                            u'【操作动作】：' + 'Closed' + '\r\n' + \
                            u'【操作时间】：' + current_time + '\r\n' + \
                            u'【操作理由】：' + u'超过7天未重现此问题，关闭此问题'
            jira.transition_issue(i, 'CLOSE', close_comment)
        else:
            print '不做操作'

def GetJenkinsVar(key):
    try:
        value = os.environ.get(key)
    except Exception:
        value = os.environ.get(key.upper())
    #print('value = ',value)
    if(not value):
        value = ''
    #print( os.path.join(r'c:/a',value) )
    return value

if True:
    from Monkey import Monkey
    download_url = GetJenkinsVar("download_url")
    config_file = "conf.ini"
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file))
    test_times = config.get("config", "test_times")
    Monkey = Monkey(download_url, test_times)
    Monkey.main()
    DB_new = DB.HandleDatabase()
    global log_dir, components_name
    log_dir, components_name = DB_new.get_all_info()
    time_count = Monkey.time_count
    time_count = str(time_count)
    current_time = Monkey.current_time
    logging.info('package name:' + Monkey.package_name)
    logging.info('time_count:' + time_count)

    # 解决重名
    if Monkey.package_name == 'com.tcl.live.avg':
        Monkey.package_name = 'com.tcl.live'
    global devices_info
    devices_info = get_device_info(Monkey.devices)
    print '----------id & info-----------'
    print Monkey.devices
    print devices_info

    if len(Monkey.devices) == 0:
        logging.info('devices_id is null')
        sys.exit(1)
    parse_log()
    txt_to_html()

    # ------------JIRA-------------#

    f = open(os.path.join(Monkey.logs_home, 'apk_version.txt'))
    apk_version = f.read().strip()

    f = open(os.path.join(Monkey.logs_home, 'count.txt'))
    test_result = f.read().split(' \r\n')
    print f.read().strip()

    jira = TJIRA.MIEJIRA()
    if True:
        details = []
        jira_create_data = {}
        type_id_by_detail = {}
        devices_by_detail = {}
        crash_count_by_detail = {}
        description_by_detail = {}
        priority_by_detail = {}
        reoccur_times_by_detail = {}
        comment_by_detail = {}

        for device_result in test_result:
            print device_result
            if device_result != '':
                detail = device_result[find_str(device_result, '|', 3) + 1:find_str(device_result, '|', 4)]
                #                 print details
                summary = '[' + Monkey.download_url.split("/")[-1].split(".")[0] + '] ' \
                          + device_result[find_str(device_result, '|', 1)
                                          + 1:find_str(device_result, '|', 2)] + '_' + \
                          device_result[find_str(device_result, '|', 3) + 1:find_str(device_result, '//', 1)]
                print '=================='
                print summary
                if len(summary) > 255:
                    summary = summary[:250] + '...'
                component = components_name[Monkey.package_name]
                #                 component = 'TCLTEST'

                crash_count = device_result[find_str(device_result, '|', 4) + 1:find_str(device_result, '|', 5)]
                test_time_total = (int(time_count) * 0.2 / 60 / 60)

                reoccur_times = crash_count + u'次/' + str(test_time_total) + u'小时'
                reoccur_times_by_detail[detail] = reoccur_times
                crash_count_by_detail[detail] = crash_count

                crash_hz = int(crash_count) / test_time_total
                if 0 <= crash_hz <= 5:
                    priority = '3'
                elif 5 < crash_hz <= 10:
                    priority = '2'
                elif crash_hz > 10:
                    priority = '1'
                priority_by_detail[detail] = priority

                device_type_id = device_result[find_str(device_result, '|', 2) + 1:find_str(device_result, '|', 3)]
                type_id_by_detail[detail] = device_type_id

                crash_devices = device_result[device_result.rindex('|') + 1:]
                devices_by_detail[detail] = crash_devices

                description = get_description(device_result, device_type_id)
                description_by_detail[detail] = description

                comment = u'=================================================================================\r\n' + \
                          u'【项目名称】：' + Monkey.download_url.split("/")[-1].split(".")[0] + '\r\n' + \
                          u'【测试版本】：' + apk_version.strip() + '\r\n' + \
                          u'【测试时间】：' + current_time + '\r\n' + \
                          u'【crash次数】：' + reoccur_times + '\r\n' + \
                          description
                comment_by_detail[detail] = comment
                print detail
                print (summary, description, component, reoccur_times, comment, priority)
                if not filter(lambda x: jira_create_data[x][0] == summary or len(filter(lambda x: x in summary.split(" "), jira_create_data[x][0].split(" "))) == len(jira_create_data[x][0].split(" ")) - 1, jira_create_data.keys()):
                    details.append(detail)
                    jira_create_data[detail] = (summary, description, component, reoccur_times, comment, priority)

        query_result = DB_new.query_db(Monkey.download_url.split("/")[-1].split(".")[0].decode("utf-8"), details)

        # print query_result
        create_result = []
        insert_data = []
        temp = ()
        for detail in details:
            print query_result[detail]
            # print type(query_result[detail])
            if query_result[detail] == temp:
                create_data = jira_create_data[detail]
                # print detail
                # print create_data
                # print apk_versions
                jira_create_return = jira.create_issue(create_data[0], create_data[1],
                                                       create_data[2], create_data[3],
                                                       apk_version, create_data[4], create_data[5])
                print jira_create_return
                insert_data.append((Monkey.download_url.split("/")[-1].split(".")[0], apk_version, type_id_by_detail[detail], detail,
                                    crash_count_by_detail[detail], devices_by_detail[detail],
                                    jira_create_return['issue_key'], current_time))
            else:
                # query_db返回键值对，其中值是元组嵌套
                jira_key = query_result[detail]["jira_key"]
                print jira.query_issue_bykey((jira_key,))
                jira_status = jira.query_issue_bykey((jira_key,))[jira_key][0]
                print jira_status
                old_version = jira.query_issue_bykey((jira_key,))[jira_key][2].replace('\n', '')
                new_version = apk_version.replace('\n', '')
                print old_version
                print new_version

                if compare_version(old_version, new_version) < 0:
                    if jira_status == 'Solved' or jira_status == 'Closed':
                        jira.update_issue(jira_key, description_by_detail[detail], apk_version,
                                          priority_by_detail[detail],
                                          reoccur_times_by_detail[detail], comment_by_detail[detail])
                        print '----------------reopen---------------'
                        jira.transition_issue(jira_key, 'REOPEN')
                    else:  # 其他状态只更新值
                        jira.update_issue(jira_key, description_by_detail[detail], apk_version,
                                          priority_by_detail[detail],
                                          reoccur_times_by_detail[detail], comment_by_detail[detail])
                insert_data.append((Monkey.download_url.split("/")[-1].split(".")[0], apk_version, type_id_by_detail[detail], detail,
                                    crash_count_by_detail[detail], devices_by_detail[detail],
                                    jira_key, current_time))

        if len(insert_data) > 0:
            DB_new.insert_db(insert_data)
    # sys.exit(0)
    close_bug()
    DB_new.close()
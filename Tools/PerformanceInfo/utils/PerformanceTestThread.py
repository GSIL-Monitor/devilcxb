# -*- coding: utf-8 -*-
import ConfigParser
import os
import subprocess
import time
import openpyxl
from utils.openpyxlUtil import WriteReport
from appInfo import appInfo
import threading

__author__ = 'wei.y'

devices_data_path = r"/sdcard/PerformanceTest/"
traffic_dir = r'/sdcard/trafficStats'
performance_apk_info = {'apk_name': 'performanceInfo.apk', 'packageName': 'com.tcl.tcltrafficstats',
                        'mainActivity': 'com.tcl.tcltrafficstats.MainActivity'}


def exe_cmd(cmd, shell=False, timeout=600, stdout_type=subprocess.SW_HIDE):
    """
        执行cmd命令
    :param cmd: 命令
    :param shell: 是否已shell执行
    :param timeout: 命令执行超时时间
    :param stdout_type: 结果输出类型
    :return:
    """
    print cmd
    p = subprocess.Popen(cmd, shell=shell, stdout=stdout_type, stderr=stdout_type)
    times = 0
    desc = ''
    while True:
        if p.poll() is not None:
            break
        if timeout <= times:
            p.terminate()
            desc = u'执行超时退出'
            break
        times += 1
        time.sleep(1)
    if subprocess.PIPE == stdout_type:
        stdout, stderr = p.communicate()
        print 'stderr: ' + stderr
        return stdout
    time.sleep(1)
    return {'returncode': p.returncode, "desc": desc}


class AppCmdUtils(object):
    def __init__(self, devices_no):
        if devices_no:
            self.device_no = devices_no
            self.adb_head = 'adb -s %s ' % devices_no
        else:
            self.device_no = None
            self.adb_head = 'adb '

    def get_uid(self, package_name):
        cmd = '%s shell "ps |grep %s "' % (self.adb_head, package_name)
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
            cmd = '%s shell "cat /proc/%s/status |grep Uid' % (self.adb_head, pid)
            cat_uid_infos = exe_cmd(cmd, stdout_type=subprocess.PIPE)
            if cat_uid_infos:
                uid_infos = cat_uid_infos[0].replace('\r\r\n', '').split('\t')
                return uid_infos[1]
        return ''

    def get_output_datas(self, result_file_path):
        """
            组装解析结果文件内容
        :param result_file_path:
        :return:
        """
        info = self.get_performance_datas(result_file_path)
        datas = []
        if info:
            datas.append(info.get('number'))
            datas.append(info.get('cpu'))
            datas.append(info.get('Mem'))
            datas.append(info.get('Tx'))
            datas.append(info.get('Rx'))
        return datas


    def get_performance_datas(self, file_path):
        """
            组装解析流量文件内容
        :param result_file_path:
        :return:
        """
        number_list = ['nums']
        time_list = ['times']
        RX_list = ['rx_datas(bytes)']
        TX_list = ['tx_datas(bytes)']
        Mem_list = ['Mems(K)']
        cpu_list = ['cpu(%)']
        traffic_dict = {}
        if os.path.exists(file_path):
            with open(file_path) as traffic_file:
                infos = traffic_file.readlines()
            total_rx = 0
            total_tx = 0
            start_rx_data = 0
            start_tx_data = 0
            total_mem = 0
            for i in xrange(len(infos)):
                array_info = infos[i].replace('\n', '').split('    ')
                number_list.append(i)
                if len(array_info) >= 4:
                    rx = float(array_info[1])
                    tx = float(array_info[2])
                    if i == 0:
                        start_rx_data = rx
                        start_tx_data = tx
                    time_list.append(array_info[0])
                    RX_list.append(rx - start_rx_data)
                    TX_list.append(tx - start_tx_data)
                    Mem_list.append(float(array_info[3]))
                    cpu_list.append(float(array_info[4].replace('%', '')))
                    total_rx += rx - start_rx_data
                    total_tx += tx - start_tx_data
                    start_rx_data = rx
                    start_tx_data = tx
                    total_mem += float(array_info[3])
                else:
                    time_list.append(' ')
                    RX_list.append(' ')
                    Mem_list.append(' ')
            traffic_dict = {'number': number_list, 'time': time_list, 'Rx': RX_list, 'Tx': TX_list, 'Mem': Mem_list,
                            'total_rx': total_rx, 'total_tx': total_tx, 'total_mem': total_mem, 'cpu': cpu_list}
        else:
            print 'file not exist'

        return traffic_dict

    def is_monkey_test_success(self, result_file_path):
        """
            组装解析流量文件内容
        :param result_file_path:
        :return:
        """
        result = True
        with open(result_file_path) as f:
            lines = f.readlines()
        for line in lines:
            if 'CRASH:' in line:
                result = False
                break
        return result

    def get_appinfos(self, apk_file_path):
        """
        反编译apk文件，获取apk信息

        :return:
        """
        app_info = appInfo().getInfo(apk_path=apk_file_path)
        if app_info and app_info.get('packageName'):
            return app_info
        else:
            tmp = os.popen(
                'java -jar appInfo.jar %s' % apk_file_path).readlines()
            print tmp
            for info in tmp:
                tmp_info = info.replace('\n', '').replace(' ', '').split(':')
                import urllib
                app_info[tmp_info[0]] = urllib.unquote(tmp_info[1])

        if app_info and app_info.get('packageName') and app_info.get('mainActivity'):
            return app_info
        else:
            return None

    def install_app(self, apk_file_path, g_param=''):
        """
            安装apk

        """

        cmd = '%s install %s -r %s' % (self.adb_head, g_param, apk_file_path)
        print exe_cmd(cmd, stdout_type=subprocess.PIPE)

    def run_monkey(self, result_path, app_package_name, monkey_result_file_path=None,
                   count='2000', device_no=None):

        """
        执行monkey命令并收集相关数据
        :param result_file:
        :param app_package_name:
        :param count:
        """
        if not device_no:
            device_no = self.device_no
        if not self.is_collecting_app_installed():
            # self.install_collecting_data_app(os.path.join(os.getcwd(), performance_apk_info.get('apk_name')))
            self.install_collecting_data_app()
        self.print_install_app()
        self.start_collecting_data_app()
        exe_cmd('adb devices')
        testThread = PerformanceTestThread(app_package_name, result_file=result_path, device=device_no,
                                           count=count, monkey_result_file_path=monkey_result_file_path)
        testThread.setDaemon(True)
        testThread.start()
        testThread.join()
        exe_cmd('adb kill-server')
        self.kill_collecting_data_app()
        self.download_static_test_result_file(result_filepath=result_path, package_name=app_package_name)

    def start_app(self, appinfo):
        start_app = "%s shell am start -n %s/%s" % (
            self.adb_head, appinfo.get('packageName'), appinfo.get('mainActivity'))
        exe_cmd(start_app)

    def keyevent(self, keycode):
        cmd = '%s shell input keyevent %s ' % (self.adb_head, keycode)
        exe_cmd(cmd)

    def reboot_phone(self):
        cmd = '%s reboot ' % self.adb_head
        print exe_cmd(cmd, stdout_type=subprocess.PIPE)

    def uninstall_app(self, app_package_name):
        cmd = '%s uninstall %s' % (self.adb_head, app_package_name)
        print exe_cmd(cmd, stdout_type=subprocess.PIPE)

    def install_collecting_data_app(self,
                                    apk_file_path=os.path.join(os.getcwd(), performance_apk_info.get('apk_name'))):
        adb_version = exe_cmd('%s shell getprop ro.build.version.sdk' % self.adb_head, stdout_type=subprocess.PIPE)
        if int(adb_version) >= 23:
            self.install_app(apk_file_path=apk_file_path, g_param='-g')
        else:
            self.install_app(apk_file_path=apk_file_path)

    def push_test_conf_file(self):
        device_conf_path = "%s/conf.txt" % traffic_dir
        local_conf_path = "conf/conf.txt"
        push_cmd = '%s push %s %s' % (self.adb_head, local_conf_path, device_conf_path)
        exe_cmd(push_cmd)

    def is_collecting_app_installed(self, appinfo=None):
        if not appinfo:
            appinfo = performance_apk_info
        cmd = '%s  shell "pm list package| grep %s" ' % (self.adb_head, appinfo.get('packageName'))
        result_strs = exe_cmd(cmd=cmd, stdout_type=subprocess.PIPE)
        if result_strs:
            return True
        return False

    def print_install_app(self):
        appinfo = performance_apk_info
        cmd = '%s  shell "pm list package| grep %s" ' % (self.adb_head, appinfo.get('packageName'))
        result_strs = exe_cmd(cmd=cmd, stdout_type=subprocess.PIPE)
        print 'installed collection app info', result_strs

    def start_collecting_data_app(self):
        appinfo = performance_apk_info
        self.start_app(appinfo=appinfo)

    def kill_collecting_data_app(self):
        time.sleep(10)
        cmd = '%s shell am force-stop %s' % (self.adb_head, performance_apk_info.get('packageName'))
        exe_cmd(cmd)

    def download_static_test_result_file(self, package_name, result_filepath):
        pull_tf_cmd = '%s pull %s/%s.txt %s' % (self.adb_head, traffic_dir, package_name, result_filepath)
        print 'download_test_result ', exe_cmd(pull_tf_cmd, subprocess.PIPE)


class PerformanceTestThread(threading.Thread):
    def __init__(self, test_packageName, result_file, device=None, count='20000', monkey_result_file_path=None):
        super(PerformanceTestThread, self).__init__()
        self.packageName = test_packageName
        self.device = device
        self.count = count
        self.result_file = result_file
        self.monkey_result_file_path = monkey_result_file_path

    def run(self):
        exe_cmd(self.get_monkey_cmd(), shell=True)

    def get_top_cmd(self, interval_time='1'):
        top_cmd = 'adb '
        if self.device:
            top_cmd += '-s ' + self.device
        top_cmd += ' shell "top -d %s |grep %s" >%s ' % (interval_time, self.packageName, self.result_file)
        return top_cmd

    def get_monkey_cmd(self, monkey_test_result_path=None):
        monkey_cmd = 'adb '
        if self.device:
            monkey_cmd += '-s ' + self.device
        if not monkey_test_result_path:
            result_dir = self.result_file.replace('/', '\\').rsplit('\\', 1)[0]
            monkey_test_result_path = os.path.join(result_dir, 'monkey_test_result.txt')
        monkey_cmd += ' shell monkey --pct-touch 100 --monitor-native-crashes -p %s --throttle 300 -v -v %s > %s' % (
            self.packageName, self.count, monkey_test_result_path)
        return monkey_cmd


def mk_result_dir(device_no):
    """
        创建测试结果存放文件夹
    :param device_no:
    :return:
    """
    path_name = '%s_%s' % (time.strftime('%Y%m%d%H%M%S', time.localtime()), device_no)
    result_path = os.path.join('result', path_name)
    os.mkdir(result_path)
    return result_path


def get_config_info(config_file_path):
    """
        解析测试配置文件
    :param config_file_path:
    :return:
    """
    cf = ConfigParser.ConfigParser()
    cf.read(config_file_path)
    global_dict = {}
    end_section = cf.sections()[-1]
    options = cf.options(end_section)
    for option in options:
        global_dict[option] = cf.get(end_section, option)

    app_sections = cf.sections()[0:-1]
    app_config_list = []
    for section in app_sections:
        app_dict = {}
        app_options = cf.options(section)
        for option in app_options:
            app_dict[option] = cf.get(section, option)
        app_config_list.append(app_dict)

    return app_config_list, global_dict


def get_all_evn_info():
    """
        获取测试配置信息，并初始化结果文件
    :return:
    """
    conf_info = get_config_info('conf/conf.ini')
    monkey_count = conf_info[-1].get('monkey_count')
    run_times = int(conf_info[-1].get('times'))
    app_test_infos = conf_info[0]
    list_all_info = []
    for app_test_info in app_test_infos:
        device_no = app_test_info.get('device')
        app_path_list = str(app_test_info.get('app_paths')).split(';')
        path_dir = mk_result_dir(device_no)
        run_app_info_dict = {'device_no': device_no, 'path_dir': path_dir, 'monkey_count': monkey_count,
                             'run_times': run_times}
        list_app_infos = []
        for apk_path in app_path_list:
            if apk_path:
                main = AppCmdUtils(device_no)
                appinfo = main.get_appinfos(apk_path)
                dynamical_result_path = os.path.join(path_dir,
                                                     'dynamical_result_%s.txt' % appinfo.get('packageName'))
                static_result_path = os.path.join(path_dir, 'static_result_%s.txt' % appinfo.get('packageName'))
                monkey_test_result_path = os.path.join(path_dir, 'monkey_test_result.txt')
                with open(dynamical_result_path, 'w') as f:
                    pass
                with open(static_result_path, 'w') as f:
                    pass

                app_info_dict = {'appinfo': appinfo,
                                 'dynamical_result_path': dynamical_result_path,
                                 'static_result_path': static_result_path,
                                 'monkey_test_result_path': monkey_test_result_path,
                                 'apk_path': apk_path}
                list_app_infos.append(app_info_dict)
        run_app_info_dict['app_infos'] = list_app_infos
        list_all_info.append(run_app_info_dict)
    return list_all_info


def run_collecting_data_app(appinfos, testtimes, appCmdUtils, apk_path=None):
    """
        应用置于后台性能数据收集
    :param apk_path:
    :param appinfos:
    :param testtimes:
    :param appCmdUtils:
    """
    packageNames = ''
    for app_info in appinfos:
        appinfo = app_info.get('appinfo')
        packageNames += appinfo.get('packageName')
        appCmdUtils.start_app(appinfo)
        test_times = int(testtimes) * 1000
        with open("conf/conf.txt", "w+") as f:
            f.write("packageName=%s\n" % packageNames)
            f.write("time=%d" % test_times)
        appCmdUtils.push_test_conf_file()
    if not appCmdUtils.is_collecting_app_installed():
        appCmdUtils.install_collecting_data_app(apk_path)
    else:
        appCmdUtils.kill_collecting_data_app()
    appCmdUtils.start_collecting_data_app()
    time.sleep(testtimes + 60)
    for app_info in appinfos:
        appCmdUtils.download_static_test_result_file(package_name=app_info.get('appinfo').get('packageName'),
                                                     result_filepath=app_info.get('static_result_path'))


def dynamical_run(appCmdUtils, result_path, packageName, apk_path, run_times=300, monkey_count='2000'):
    """
        运行动态测试数据收集
    :param appCmdUtils:
    :param result_path:
    :param packageName:
    :param apk_path:
    :param run_times:
    """
    appCmdUtils.install_app(apk_path)
    run_times = int(run_times) * 1000
    with open("conf/conf.txt", "w+") as f:
        f.write("packageName=%s\n" % packageName)
        f.write("time=%d" % run_times)
    appCmdUtils.push_test_conf_file()
    appCmdUtils.run_monkey(result_path, packageName, count=monkey_count)


def static_run(appCmdUtils, appinfos, run_times):
    # appCmdUtils.reboot_phone()
    # time.sleep(3 * 60)
    """
    运行静态测试数据收集
    :param appCmdUtils:
    :param appinfos:
    :param run_times:
    """
    for appinfo in appinfos:
        appCmdUtils.start_app(appinfo)
        appCmdUtils.keyevent('3')
        time.sleep(2)
    run_collecting_data_app(appinfos=appinfos,
                            testtimes=run_times, appCmdUtils=appCmdUtils)
    appCmdUtils.kill_collecting_data_app()


def write_datas(dynamical_datas, static_data, wb):
    """
        填写测试数据到excel中
    :param dynamical_datas:
    :param static_data:
    :param wb:
    """
    obj = WriteReport(dynamical_datas, wb, save_sheet_name=u'运行时过程数据')
    obj.write_data()
    for i in xrange(1, len(dynamical_datas)):
        obj.add_Chart(data_col_index=i + 1, chart_location='F' + str(5 + 17 * (i - 1)),
                      chart_title=dynamical_datas[i][0])

    obj1 = WriteReport(static_data, wb, save_sheet_name=u'静止后台过程数据')
    obj1.write_data()
    for i in xrange(1, len(static_data)):
        obj1.add_Chart(data_col_index=i + 1, chart_location='F' + str(5 + 17 * (i - 1)), chart_title=static_data[i][0])


def run_apps(infos):
    """
        运行单个手机预装应用数据收集
    :param infos:
    """
    device_no = infos.get('device_no')
    app_infos = infos.get('app_infos')
    run_times = infos.get('run_times')  # 持续时间
    path_dir = infos.get('path_dir')
    monkey_count = infos.get('monkey_count')
    appCmdUtils = AppCmdUtils(device_no)
    for app_info in app_infos:
        appinfo = app_info.get('appinfo')
        dynamical_run(appCmdUtils=appCmdUtils, result_path=app_info.get('dynamical_result_path'),
                      packageName=appinfo.get('packageName'),
                      apk_path=app_info.get('apk_path'),
                      run_times=run_times,
                      monkey_count=monkey_count)
    static_run(appCmdUtils=appCmdUtils, appinfos=app_infos, run_times=run_times)

    from runScan import runScan
    runScan().safe_scan(device_no, path_dir)
    print 'path_dir--------------------->', path_dir

    for all_app_info in app_infos:
        appinfo = all_app_info.get('appinfo')
        dynamical_datas = appCmdUtils.get_output_datas(all_app_info.get('dynamical_result_path'))
        static_datas = appCmdUtils.get_output_datas(all_app_info.get('static_result_path'))
        wb = openpyxl.Workbook()
        write_datas(dynamical_datas, static_datas, wb)

        from file_writer import file_writer
        fw = file_writer()
        dynamical_cpu_result = {'result_index': 'G3',
                                'desc_index': 'H3',
                                'desc_Data': ''}
        dynamical_mem_result = {'result_index': 'G5',
                                'desc_index': 'H5',
                                'desc_Data': ''}
        static_cpu_result = {'result_index': 'G4',
                             'desc_index': 'H4',
                             'desc_Data': ''}
        static_mem_result = {'result_index': 'G6',
                             'desc_index': 'H6',
                             'desc_Data': ''}
        static_traffic_result = {'result_index': 'G7',
                                 'desc_index': 'H7',
                                 'desc_Data': ''}
        list_results = [dynamical_cpu_result, dynamical_mem_result, static_cpu_result, static_mem_result,
                        static_traffic_result]
        monkey_result = appCmdUtils.is_monkey_test_success(all_app_info.get('monkey_test_result_path'))
        if not monkey_result:
            list_results[0] = u'monkey 测试过程中出现crash'
            list_results[1] = u'monkey 测试过程中出现crash'
        fw.save_file(path_dir, device_no, appinfo, wb, list_results)
        wb.save('%s/%s.xlsx' % (path_dir, appinfo.get('app_name')))
        appCmdUtils.uninstall_app(appinfo.get('packageName'))


if __name__ == '__main__':
    all_devices_config_infos = get_all_evn_info()
    print all_devices_config_infos
    list_thread = []
    for infos in all_devices_config_infos:
        th = threading.Thread(target=run_apps, args=(infos,))
        th.start()
        list_thread.append(th)
    for thd in list_thread:
        thd.join()

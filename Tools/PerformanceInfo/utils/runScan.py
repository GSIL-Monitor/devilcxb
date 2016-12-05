# coding:utf-8
import openpyxl, logging, os
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import subprocess, time, sys, chardet, json


class runScan():
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='safeTestLogs.log',
                            filemode='a')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def safe_scan(self, device, path):
        '''安全性扫描,jar包返回json格式数据,如:[{"name":"xxxx","result":"xxxx"}]'''
        try:
            cmd_push = 'adb -s %s push safeTester.jar /data/local/tmp' % device
            proc = subprocess.check_output(cmd_push, bufsize=0, shell=True)
            cmd_str = 'adb -s %s shell uiautomator runtest safeTester.jar -c com.tcl.safe.Main' % device
            proc = subprocess.check_output(cmd_str, bufsize=0, shell=True)
            print proc
        except subprocess.CalledProcessError, e:
            logging.error(e)
        try:
            rFile = device + 'Result.txt'
            path = os.path.join(path, rFile)
            out, err, returncode = self.run_command(
                r'adb -s %s pull /sdcard/scanResult.txt %s' % (device, path))
            return returncode
        except:
            s = sys.exc_info()
            logging.error('Error "%s" happened on line %d' % (s[1], s[2].tb_lineno))

    def run_command(self, command, timeout=10):
        try:
            proc = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            poll_seconds = .250
            deadline = time.time() + timeout
            while time.time() < deadline and proc.poll() == None:
                time.sleep(poll_seconds)
            if proc.poll == None:
                proc.terminate()
                stdout,stderr = ('cmd timeout','')
                return stdout,stderr,0
            stdout, stderr = proc.communicate()
            return stdout, stderr, proc.returncode
        except Exception, e:
            logging.error(e)


if __name__ == '__main__':
    runScan().safe_scan()

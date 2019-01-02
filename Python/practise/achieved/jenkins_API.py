import jenkinsapi.jenkins as jenkins
import sys
import requests
import time


class handle_jenkins(object):

    def __init__(self,jenkins_server, Username, Password, job_name, params):
        self.jenkins_server = jenkins_server
        self.Username = Username
        self.Password = Password
        self.job_name = job_name
        self.params = params
        #global server
        try:
            self.server = jenkins.Jenkins(self.jenkins_server, username=self.Username, password=self.Password)
            print "jenkins server is connected!"
        except requests.exceptions.ConnectionError:
            info=sys.exc_info()
            print info[0],":",info[1]
            sys.exit(1)

    def build_job(self):
        self.params["app_name"] = str(params["app_name"].decode("gb2312").encode("utf-8").decode("utf-8").split())[2:-1]
        self.params["appname"] = str(params["appname"].split())[2:-1]
        self.server.build_job(self.job_name, params = self.params)

    def main(self):
        self.build_job()

if __name__ == "__main__":
    jenkins_server = 'http://172.26.32.18/jenkins/'
    Username = "xiaobo.chi"
    Password = "DEVIL_cxb789"
    job_name = "app_compatibility_testing"
    params = {'app_name': '\xd3\xa6\xd3\xc3\xca\xd0\xb3\xa1', 'appname': u'\u5e94\u7528\u5e02\u573a', 'apkPath': '\\\\172.26.50.50\\AppstoreData\\upload_apk\\tclmarket-V5.1.0-2016-01-06-release_test.apk', 'packageName': 'com.tclmarket', 'list_deviceid': [u'a972d6b6'], 'mainActivity': 'com.tclmarket.sz.activity.WelcomeActivity', 'result': 0, 'versionName': '5.1.0', 'versioncode': '5.1.0', 'packagename': 'com.tclmarket', 'uid': '1'}
    params["app_name"] = str(params["app_name"].decode("gb2312").encode("utf-8").decode("utf-8").split())[2:-1]
    params["appname"] = str(params["appname"].split())[2:-1]
    handle_jenkins = handle_jenkins(jenkins_server, Username, Password, job_name, params)
    handle_jenkins.main()

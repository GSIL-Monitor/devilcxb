# coding:utf-8
import subprocess, chardet, re, os, sys


class appInfo(object):
    def __init__(self):
        # project_path = self.get_project_path()
        # aapt_path = os.path.join(project_path,'buz','Utils','')
        self.aapt_path = os.path.join('')

    def getInfo(self, apk_path):
        app_dict = {}
        output = subprocess.check_output(self.aapt_path + 'aapt d badging ' + apk_path)
        lines = output.split('\r\n')
        for i in lines:
            if i.startswith('package:'):
                packageName_regx = re.compile(".*name='(.*?)'\s")
                version_regx = re.compile(".*versionName='(.*?)'\s")
                packageName_match = packageName_regx.match(i)
                version_match = version_regx.match(i)
                if packageName_match:
                    app_dict['packageName'] = packageName_match.group(1)
                if version_match:
                    app_dict['versionName'] = version_match.group(1)
            if i.startswith('application-label:'):
                regx = "application-label:'(.*)'"
                self.get_app_name(regx, app_dict, i)

            if i.startswith('application:'):
                regx = "application:\slabel='(.*)'.*icon=.*"
                self.get_app_name(regx, app_dict, i)

            if i.startswith('launchable-activity:'):
                pattern = re.compile(".*name='(.*)'.*label=.*")
                match = pattern.match(i)
                if match:
                    app_dict['mainActivity'] = match.group(1)
                if not app_dict.has_key('app_name'):
                    regx = ".*label='(.*)'.*icon=.*"
                    self.get_app_name(regx, app_dict, i)

        if not app_dict.has_key('mainActivity'):
            main = self.decode_xmltree(apk_path)
            if main:
                app_dict['mainActivity'] = main

        return app_dict

    def get_app_name(self, regx, app_dict, text):
        pattern = re.compile(regx)
        match = pattern.match(text)
        if match:
            rs = match.group(1)
            if not rs == '':
                app_dict['app_name'] = rs.decode('utf8')
        return app_dict

    def decode_xmltree(self, apk_path):
        try:
            output = subprocess.check_output(self.aapt_path + 'aapt d xmltree ' + apk_path + ' AndroidManifest.xml')
            lines = output.split('\r\n')
            read_lines = []
            tmp_lines = []
            pattern = re.compile('.*E:.*activity|.*E:.*activity-alias')
            for i in lines:
                match = pattern.match(i)
                if match and tmp_lines:
                    if pattern.match(tmp_lines[0]):
                        read_lines.append(tmp_lines)
                    tmp_lines = []
                tmp_lines.append(i.strip())
            read_lines.append(tmp_lines)

            regx_name = '.*?A:\sandroid:name\(0x01010003\)="(.*?)"\s\('
            mainActivity_dict = {}
            for j in read_lines:
                isMainActivity = 0
                read_line = ','.join(j)
                split_str = 'E: intent-filter'
                if split_str in read_line:
                    infos = read_line.split(split_str)
                    if 'android.intent.action.MAIN' in infos[1] and 'android.intent.category.LAUNCHER' in infos[1]:
                        pattern = re.compile(regx_name)
                        match = pattern.match(infos[0])
                        if match:
                            if 'android.intent.category.DEFAULT' in infos[1]:
                                mainActivity_dict['2'] = match.group(1)
                            else:
                                mainActivity_dict['1'] = match.group(1)

            if mainActivity_dict.has_key('2'):
                return mainActivity_dict['2']
            elif mainActivity_dict.has_key('1'):
                return mainActivity_dict['1']
        except:
            s = sys.exc_info()
            print "Error %s happened in line %d" % (s[1], s[2].tb_lineno)


            # if __name__ == '__main__':
            # print appInfo().getInfo(r'D:\tools\ApkTool\apktool\com.amazon.mShop.android_5070202_7584.apk')

# -*- coding: cp936 -*-
import urllib
import urllib2
import cookielib
import re
import datetime
import xlrd
import xlwt
import sys
import subprocess
from selenium import webdriver
import time

class Test(object):
    def __init__(self):

        params = {
        "start":"2015-12-23 00:00",
        "end":"2016-1-6 00:00",
        "status":"-1", # 默认-1选择全部状态 测试完成：2，等待测试:0,正在测试:1,取消测试:3,检测不通过:4
        "result":"-1" # 默认-1选择全部结果 安装失败:0,执行失败:1
        }
        userName = "testCD"
        password = "Aa123456"
        self.driver = webdriver.Firefox()
        self.driver.get("http://tcltest.tclclouds.com/ttc/view/login.jsp")
        time.sleep(3)
        self.driver.maximize_window() # 浏览器全屏显示
        #通过用户名密码登陆
        self.driver.find_element_by_id("jiraName").send_keys(userName)
        self.driver.find_element_by_id("jiraPwd").send_keys(password)
        self.driver.find_element_by_class_name("btn-primary").click()
        #获取cookie信息并打印
        cookie= self.driver.get_cookies()
        print cookie
        time.sleep(2)
        opener = urllib.URLopener()
        opener.addheader('Cookie',cookie[0]['name'] + "=" + cookie[0]['value'])
        params = urllib.urlencode(params)
        url = "http://tcltest.tclclouds.com/ttc/record/export?" + params
        r = opener.open(url).read()
        try:                        
            F = open("TestIn_result.xls", "wb")
            F.writelines(r)
            F.close()
        except IOError:
            self.kill_process("EXCEL.EXE")
            F = open("TestIn_result.xls", "wb")
            F.writelines(r)
            F.close()
        global TestIn_File, Manual_File
        TestIn_File = xlrd.open_workbook("TestIn_result.xls")
        Manual_File = xlrd.open_workbook("第三方app测试结果（AppStore ) 2015.12.23~2016.1.5 .xls")
        
    def kill_process(self,process_name):
        output = subprocess.Popen(['tasklist', '/FI', 'IMAGENAME eq ' + process_name], stdout=subprocess.PIPE).communicate()[0]
        try:
            pid = filter(lambda x: process_name in x, output.split("\n"))[0].split()[1]
            print pid
            output = subprocess.Popen(['taskkill ', '/F','/PID', pid], stdout=subprocess.PIPE).communicate()[0]
            if "成功: 已终止 PID 为 " + pid + " 的进程" not in output:
                print process_name + " is not killed successfully!"
                sys.exit(1)
        except IndexError:
            print process_name + " process is not found!"
            sys.exit(1)
        print process_name + " is killed successfully!"
        
    def open_File(self,File):
        try:
            table = File.sheets()[0]
        except xlrd.XLRDError:
            print "close the xls file firstly!"
            kill_process("EXCEL.EXE")
            table = File.sheets()[0]
        return table
        
    def get_col_num(self,table, keyword,title_number = 0):
        return table.row_values(title_number).index(keyword)

    def get_col_result(self,table,col_num):
        return table.col_values(col_num)

    def set_style(self,name,height,bold=False):
        style = xlwt.XFStyle() # 初始化样式
        font = xlwt.Font() # 为样式创建字体
        font.name = name # 'Times New Roman'
        font.bold = bold
        font.color_index = 4
        font.height = height 
        style.font = font
        return style

    def write_excel(self, same_packages, test_result_TestIn_final, test_result_Manual_final):
        f = xlwt.Workbook(style_compression=2)
        sheet = f.add_sheet("Result",cell_overwrite_ok=True)
        count = 0
        while count < len(same_packages):
            if count == 0:
                bold = True
            else:
                bold = False
            sheet.write(count,0,same_packages[count],self.set_style('Times New Roman',220,bold))
            sheet.write(count,1,test_result_TestIn_final[count],self.set_style('Times New Roman',220,bold))
            sheet.write(count,2,test_result_Manual_final[count],self.set_style('Times New Roman',220,bold))
            count += 1
        f.save("result.xls")
        
    def main(self):
        table_TestIn = self.open_File(TestIn_File)
        col_num_test_result_TestIn = self.get_col_num(table_TestIn, u"检测状态",0)
        test_result_TestIn = self.get_col_result(table_TestIn,col_num_test_result_TestIn)[1:]
        col_num_package_name_TestIn = self.get_col_num(table_TestIn,u"包名",0)
        package_names_TestIn = self.get_col_result(table_TestIn,col_num_package_name_TestIn)[1:]

        table_Manual = self.open_File(Manual_File)
        col_num_test_result_Manual = self.get_col_num(table_Manual, u"是否已经测试",0)
        test_result_Manual = self.get_col_result(table_Manual,col_num_test_result_Manual)[1:]
        #print test_result_Manual
        try:
            col_num_package_name_Manual = self.get_col_num(table_Manual,u"packageName",1)
        except ValueError:
            col_num_package_name_Manual = self.get_col_num(table_Manual,u"packageName",0)
        package_names_Manual = self.get_col_result(table_Manual,col_num_package_name_Manual)[1:]
        #print package_names_Manual
        same_packages = ["package_Name"]
        same_packages = same_packages + filter(lambda x: x in package_names_Manual, package_names_TestIn)
        test_result_TestIn_final = ["Test_result_TestIn"]
        test_result_Manual_final = ["test_result_Manual"]
        for package in same_packages[1:]:
            test_result_TestIn_final.append(test_result_TestIn[package_names_TestIn.index(package)])
            test_result_Manual_final.append(test_result_Manual[package_names_Manual.index(package)])
        self.write_excel(same_packages, test_result_TestIn_final, test_result_Manual_final)
        self.driver.close()
        print "Finished!"
        
if __name__ == "__main__":
    Test = Test()
    Test.main()

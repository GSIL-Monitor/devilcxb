#coding=utf-8
import urllib2
import urllib
import cookielib
from selenium import webdriver
import time

driver = webdriver.Firefox()
driver.get("http://tcltest.tclclouds.com/ttc/view/login.jsp")

time.sleep(3)
driver.maximize_window() # 浏览器全屏显示

#通过用户名密码登陆
driver.find_element_by_id("jiraName").send_keys("testCD")
driver.find_element_by_id("jiraPwd").send_keys("Aa123456")
driver.find_element_by_class_name("btn-primary").click()
#获取cookie信息并打印
cookie= driver.get_cookies()
print cookie
time.sleep(2)

opener = urllib.URLopener()
# Add headers for urllib
opener.addheader('Cookie',cookie[0]['name'] + "=" + cookie[0]['value'])
url = "http://tcltest.tclclouds.com/ttc/record/export?appname=&status=-1&result=-1&start=2015-12-25 00:00&end=2015-12-25 18:00"
opener.retrieve()
r = opener.open(url).read()
F = open("test.xls", "wb")
F.writelines(r)
F.close()
driver.close()

# urllib2 will have 505 error code that HTTP version is not supported.
"""
opener = urllib2.build_opener()
opener.addheaders.append(('Cookie',cookie[0]['name'] + "=" + cookie[0]['value']))
urllib2.install_opener(opener)
url = "http://tcltest.tclclouds.com/ttc/record/export?appname=&status=-1&result=-1&start=2015-12-25 00:00&end=2015-12-25 18:00"
f = urllib2.urlopen(url)
"""



#Demo to use cookie got from webdriver and used for urllib2
"""
driver = webdriver.Firefox()
driver.get("http://confluence.lab.tclclouds.com/display/SC?&os_username=xiaobo.chi&os_password=DEVIL_cxb123")

cookie= driver.get_cookies()
print cookie
time.sleep(2)

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie',cookie[0]['name'] + "=" + cookie[0]['value']))
urllib2.install_opener(opener)
url = "http://confluence.lab.tclclouds.com/display/SC"
#print opener.open(url).read()
print urllib2.urlopen(url).read()
driver.close()
"""

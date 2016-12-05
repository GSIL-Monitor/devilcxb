# -*- coding: cp936 -*-
import urllib
import urllib2
import cookielib
import re
import os

u = urllib2.urlopen("http://172.24.220.169/teleweb/Idol3-4.7/daily_version/vAL5-H-EU/")
for File in map(lambda x:re.findall('".*"',x)[0].replace('"', ""),re.findall('<a href=".*\..*">.*\..*</a>', u.read())):
    print File + " is starting to download!"
    url = "http://172.24.220.169/teleweb/Idol3-4.7/daily_version/vAL5-H-EU/" + File
    urllib.urlretrieve(url, r"D:\Tool\flash\idle3-4.7\vAL5-H-EU" + "\\" + File)
    print File + " is downloading finished!"
"""
u = urllib2.urlopen("http://172.24.220.169/teleweb/pixi3-5_3g/perso/1A2F/ZZ/")
for File in map(lambda x:re.findall('".*"',x)[0].replace('"', ""),re.findall('<a href=".*\..*">.*\..*</a>', u.read())):
    print File + " is starting to download!"
    url = "http://172.24.220.169/teleweb/pixi3-5_3g/perso/1A2F/ZZ/" + File
    urllib.urlretrieve(url, os.path.join(os.getcwd() + "\\" + r"Pixi3-5_3G\perso_1A2F",File))
    print File + " is downloading finished!"
"""
# -*- coding: cp936 -*-
import sys
import re
import os

File = r"D:\Others\test222.py"
#print os.path.dirname(File)
os.sys.path.append(os.path.dirname(File))
module_name = File.split("\\")[-1].replace(".py", "")
__import__(module_name) #��̬�ص���ģ��
m=sys.modules[module_name]#�õ����ģ��
#print m
attstr=dir(m)#�õ����Ե��б�

for str in attstr:
    att = getattr(m,str)
    #�������
    if type(att)==type:
        theObj=att()#ʵ����

for str in dir(theObj):
    #����������ú���
    if not re.search("__.*__", str):
        method = str
        getattr(theObj,method)()


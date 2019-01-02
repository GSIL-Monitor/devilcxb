# -*- coding: cp936 -*-
import sys
import re
import os

File = r"D:\Others\test222.py"
#print os.path.dirname(File)
os.sys.path.append(os.path.dirname(File))
module_name = File.split("\\")[-1].replace(".py", "")
__import__(module_name) #动态地导入模块
m=sys.modules[module_name]#得到这个模块
#print m
attstr=dir(m)#得到属性的列表

for str in attstr:
    att = getattr(m,str)
    #如果是类
    if type(att)==type:
        theObj=att()#实例化

for str in dir(theObj):
    #如果不是内置函数
    if not re.search("__.*__", str):
        method = str
        getattr(theObj,method)()


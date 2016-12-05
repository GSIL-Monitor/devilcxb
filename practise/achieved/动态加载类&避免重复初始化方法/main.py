# -*- coding: cp936 -*-
import sys
import re
import os
import threading

Files = ["c.py", "d.py", "e.py"]
def do_something(File,Init, Tn):
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
            #print att
            theObj=att(init=Init, tn=Tn)#实例化

    for str in dir(theObj):
       # print str
        #如果不是内置函数
        if not re.search("__.*__", str):
            method = str
            try:
                result_total.append(getattr(theObj,method)())
            except TypeError:
                pass
            except AttributeError:
                pass
            except IndexError:
                result_total.append(getattr(theObj,method)())

global result_total
result_total = []
#print os.path.dirname(File)
File = Files[0]
os.sys.path.append(os.path.dirname(File))
module_name = File.split("\\")[-1].replace(".py", "")
__import__(module_name) #动态地导入模块
m=sys.modules[module_name]#得到这个模块
#print m
attstr=dir(m)#得到属性的列表
Init = True
Tn = None
for str in attstr:
    att = getattr(m,str)
    #如果是类
    if type(att)==type:
        #print att
        theObj=att(init=Init, tn=Tn)#实例化
        Tn = theObj.tn
        Init = False

threads = []
for File in Files[1:]:
    t = threading.Thread(target=do_something,args=(File,Init,Tn))
    threads.append(t)
for t in threads:
#print time.ctime()
    t.start()
# 等待子线程结束
for t in threads:
    t.join()

Tn.close()

for i in result_total:
    print i
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
    __import__(module_name) #��̬�ص���ģ��
    m=sys.modules[module_name]#�õ����ģ��
    #print m
    attstr=dir(m)#�õ����Ե��б�
    for str in attstr:
        att = getattr(m,str)
        #�������
        if type(att)==type:
            #print att
            theObj=att(init=Init, tn=Tn)#ʵ����

    for str in dir(theObj):
       # print str
        #����������ú���
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
__import__(module_name) #��̬�ص���ģ��
m=sys.modules[module_name]#�õ����ģ��
#print m
attstr=dir(m)#�õ����Ե��б�
Init = True
Tn = None
for str in attstr:
    att = getattr(m,str)
    #�������
    if type(att)==type:
        #print att
        theObj=att(init=Init, tn=Tn)#ʵ����
        Tn = theObj.tn
        Init = False

threads = []
for File in Files[1:]:
    t = threading.Thread(target=do_something,args=(File,Init,Tn))
    threads.append(t)
for t in threads:
#print time.ctime()
    t.start()
# �ȴ����߳̽���
for t in threads:
    t.join()

Tn.close()

for i in result_total:
    print i
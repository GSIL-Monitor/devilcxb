import telnetlib
import time
import timeit

host = {}
host['ip'] = '172.26.50.37'
host['user'] = b'jenkins'
host['password'] = b'jenkins123'
host['command'] = b'cd /'
host['command1'] = b'ls /'


tn = telnetlib.Telnet(host['ip'])
tn.set_debuglevel(2)
tn.read_until(b'login ',15)
time.sleep(2)
tn.write(host['user'] + b'\n')
tn.read_until(b'Password: ',15)
time.sleep(2)
tn.write(host['password'] + b'\n')
tn.read_until(b'~$ ',5)
#tn.write(host['command'] + b'\n')      
#time.sleep(1)
#tn.read_until(b'~$ ',5)
#result = tn.read_very_eager()
#print result
#tn.write(host['command1'] + b'\n')
#time.sleep(1)
#tn.read_until(b'~$ ',5)
tn.write(b"ssh xiaobo.chi@121.40.72.69" + b'\n')
tn.read_until(b'password: ',10)
time.sleep(1)
tn.write(b"xiaobo@tcl.com" + b'\n')
tn.read_until(b'121-40-72-69 ~]$ ',10)
time.sleep(1)
tn.write(b"kinit" + b'\n')
tn.read_until(b'@TCL.COM: ',10)
time.sleep(1)
tn.write(b"DEVIL_cxb123" + b'\n')
tn.read_until(b'121-40-72-69 ~]$ ',10)
time.sleep(1)
tn.write(b"ssh xiaobo.chi@124.251.36.21" + b'\n')
tn.read_until(b'124-251-36-21 ~]$ ',10)
time.sleep(1)
tn.write(b"work" + b'\n')
tn.read_until(b'124-251-36-21 ~]$ ',10)
time.sleep(1)
tn.write(b"mysql -h192.168.0.1 -utcloud -pduolct123" + b'\n')
tn.read_until(b'mysql> ',10)
time.sleep(1)
tn.write(b"use appstore" + b'\n')
tn.read_until(b'mysql> ',10)
time.sleep(1)
tn.write(b"select count(name) from app_source where epoch=0 and status<>0;" + b'\n')
time.sleep(5)
result=tn.read_very_eager()
tn.read_until(b'mysql> ',10)
tn.close()
print result

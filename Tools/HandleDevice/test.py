import telnetlib
import time

host = {}
host['ip'] = '10.115.101.230'
host['user'] = 'jenkins'
host['password'] = 'jenkins123'


#Telnet
tn = telnetlib.Telnet(host['ip'])
tn.set_debuglevel(2)
tn.read_until('login ',15)
time.sleep(2)
tn.write(host['user'] + '\n')
tn.read_until('Password: ',15)
time.sleep(2)
tn.write(host['password'] + '\n')
tn.read_until('~$ ',5)
tn.write("ssh xiaobo.chi@121.40.72.69" + "\n")
tn.read_until('password: ',5)
tn.write("xiaobo@tcl.com" + "\n")
tn.read_until('~$ ',5)
tn.write("kinit" + "\n")
try:
    tn.read_until('Password',5)
    tn.write("DEVIL_cxb456" + "\n")
except:
    pass
tn.read_until('~$ ',5)
tn.write("ssh xiaobo.chi@124.251.36.21" + "\n")
tn.read_until('~$ ',5)
tn.write("work" + "\n")
tn.read_until('~$ ',5)
tn.write("ssh 192.168.1.236" + "\n")
tn.read_until('~$ ',5)
tn.write("startHive" + "\n")
tn.read_until('hive>  ',15)
tn.write("use sdk;" + "\n")
tn.read_until('hive>  ',15)
tn.write("select count(distinct DEVICE_ID) from dt_sdk_info where PROJECT_ID='yyql057a60' and CREATE_DAY between'2016-09-01' and '2016-09-30';" + "\n")
result = tn.read_until('hive>  ',30)
print result
print "################################"
print "result is:"
print result.split("\r\n")[result.split("\r\n").index("OK") + 1]
print "################################"
tn.close()
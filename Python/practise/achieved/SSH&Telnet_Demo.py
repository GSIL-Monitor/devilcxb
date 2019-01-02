import paramiko
import telnetlib
import time

host = {}
host['ip'] = '172.26.50.37'
host['user'] = 'jenkins'
host['password'] = 'jenkins123'

#SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host['ip'], username = host['user'], password = host['password'])
#stdin,stdout, stderr = ssh.exec_command('cd')
stdin,stdout, stderr = ssh.exec_command('cd /tmp')
stdin,stdout, stderr = ssh.exec_command('pwd')
print stdout.readlines()
stdin,stdout, stderr = ssh.exec_command('cd /tmp;pwd')
print stdout.readlines()
ssh.close()

#Telnet
tn = telnetlib.Telnet(host['ip'])
#tn.set_debuglevel(2)
tn.read_until('login ',15)
time.sleep(2)
tn.write(host['user'] + '\n')
tn.read_until('Password: ',15)
time.sleep(2)
tn.write(host['password'] + '\n')
tn.read_until('~$ ',5)
tn.write('cd /tmp' + '\n')
tn.read_until('~$ ',5)
tn.write('pwd' + '\n')
time.sleep(1)
result = tn.read_very_eager()
tn.read_until('~$ ',5)
print result.split("\r\n")
tn.write('cd /' + '\n')
tn.read_until('~$ ',5)
tn.write('cd /tmp;pwd' + '\n')
time.sleep(1)
result = tn.read_very_eager()
tn.read_until('~$ ',5)
tn.close()
print result.split("\r\n")

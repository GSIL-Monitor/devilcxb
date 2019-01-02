import telnetlib
import ConfigParser
import os
import sys
import time

class a(object):

    def __init__(self, config_File = "conf.ini"):
        self.config_File = config_File
        #if os.path.isfile(self.config_File):
            #self.nice_print("conf.ini file is existed!")
        #else:
            #self.nice_print("conf.ini file is not existed!")
            #sys.exit(1)
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.config_File))
        host = {"ip":self.config.get("telnetServer","ip"),
                "username":self.config.get("telnetServer","username"),
                "password":self.config.get("telnetServer","password"),
                "kerber_ip":self.config.get("kerber","based_ip"),
                "kerber_username":self.config.get("kerber","username"),
                "kerber_password":self.config.get("kerber","password"),
                "kinit_password":self.config.get("kerber","kinit_password"),
                "server_ip":self.config.get("kerber","server_ip")
        }
        self.tn = telnetlib.Telnet(host['ip'])
        #self.tn.set_debuglevel(2)
        self.tn.read_until(b'login ',15)
        time.sleep(1)
        self.tn.write(host['username'] + b'\n')
        self.tn.read_until(b'Password: ',15)
        time.sleep(1)
        self.tn.write(host['password'] + b'\n')
        self.tn.read_until(b'~$ ',5)

    def nice_print(self, message, sign='*'):
        '''
            Printing nice banners
        '''
        print(''.join([' ', sign*len(message)]))
        print(''.join([' ', message]))
        print(''.join([' ', sign*len(message)]))
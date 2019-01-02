import MySQLdb
import telnetlib
import paramiko
import ConfigParser
import os
import sys
import time


class GetSqlResult(object):
    def __init__(self, config_File = "conf.ini"):
        self.config_File = config_File
        if os.path.isfile(self.config_File):
            self.nice_print("conf.ini file is existed!")
        else:
            self.nice_print("conf.ini file is not existed!")
            sys.exit(1)
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.config_File))
        self.host_sql = {"ip":self.config.get("database","ip"),
                        "user":self.config.get("database","username"),
                        "passwd":self.config.get("database","password"),
                        "db":self.config.get("database","default_schema"),
                        "charset":"gb2312",
                        "port":int(self.config.get("database","port"))
                         }

    def nice_print(self, message, sign='*'):
        '''
            Printing nice banners
        '''
        print(''.join([' ', sign*len(message)]))
        print(''.join([' ', message]))
        print(''.join([' ', sign*len(message)]))

    def connection_MySQLdb(self, sqls):
        result = []
        db_con = MySQLdb.connect(host=self.host_sql["ip"],user=self.host_sq["user"],passwd=self.host_sq["passwd"],db=self.host_sq["db"],charset=self.host_sq["charset"],port=self.host_sq["port"])
        db_cursor = db_con.cursor()
        for sql in sqls:
            db_cursor.execute(sql)
            result.append(db_cursor.fetchall())
        db_cursor.close()
        db_con.close()
        return result

    def connection_telnet(self, sqls):
        result = []
        host = {"ip":self.config.get("telnetServer","ip"),
                "username":self.config.get("telnetServer","username"),
                "password":self.config.get("telnetServer","password"),
                "kerber_ip":self.config.get("kerber","based_ip"),
                "kerber_username":self.config.get("kerber","username"),
                "kerber_password":self.config.get("kerber","password"),
                "kinit_password":self.config.get("kerber","kinit_password"),
                "server_ip":self.config.get("kerber","server_ip")
        }
        tn = telnetlib.Telnet(host['ip'])
        tn.set_debuglevel(2)
        tn.read_until(b'login ',15)
        time.sleep(1)
        tn.write(host['username'] + b'\n')
        tn.read_until(b'Password: ',15)
        time.sleep(1)
        tn.write(host['password'] + b'\n')
        tn.read_until(b'~$ ',5)
        tn.write(b"ssh " + host["kerber_username"] + b"@" + host["kerber_ip"] + b'\n')
        tn.read_until(b'password: ',10)
        time.sleep(1)
        tn.write(host["kerber_password"] + b'\n')
        tn.read_until(host["kerber_ip"].replace(".", "-") + b'~]$ ',10)
        time.sleep(1)
        tn.write(b"kinit" + b'\n')
        tn.read_until(b'@TCL.COM: ',10)
        time.sleep(1)
        tn.write(host["kinit_password"] + b'\n')
        tn.read_until(host["kerber_ip"].replace(".", "-") + b'~]$ ',10)
        time.sleep(1)
        tn.write(b"ssh " + host["kerber_username"] + b"@" + host["server_ip"] + b'\n')
        tn.read_until(host["server_ip"].replace(".", "-") + b'~]$ ',10)
        time.sleep(1)
        tn.write(b"work" + b'\n')
        tn.read_until(host["server_ip"].replace(".", "-") + b'~]$ ',10)
        time.sleep(1)
        tn.write(b"mysql -h" + self.host_sql["ip"] + " -u" + self.host_sql["user"] + " -p" + self.host_sql["passwd"] + " -P " + str(self.host_sql["port"]) + " -D " + self.host_sql["db"] + " --default-character-set=" + self.host_sql["charset"] + b'\n')
        tn.read_until(b'mysql> ',10)
        time.sleep(1)
        for sql in sqls:
            if ";" != sql[-1]:
                sql = sql + ";"
            tn.write(sql + b'\n')
            temp_result = tn.read_until(b'mysql> ',20)
            result.append(temp_result.split("\r\n"))
        tn.close()
        return result

    def main(self):
        result = []
        database_location = self.config.get("database","location")
        print database_location
        sqls = map(lambda x: x[1], filter(lambda x:"sql" in x[0], self.config.items("socket&sql")))
        if len(sqls) == 0:
            self.nice_print("not sql found, please check your conf.ini!")
            sys.exit(1)
        if database_location == "develop":
            result.append(self.connection_MySQLdb(sqls))
        elif database_location == "test" or database_location == "online":
            print self.connection_telnet(sqls)
        else:
            self.nice_print("please specify the test environment of database as location!")
            sys.exit(1)

if __name__ == "__main__":
    GetSqlResult = GetSqlResult("conf.ini")
    GetSqlResult.main()

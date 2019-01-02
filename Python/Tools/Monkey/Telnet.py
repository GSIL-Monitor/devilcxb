import sys
import time
import telnetlib
import ConfigParser


class Telnet(object):
    
    def __init__(self):
        # config_file = os.path.join(os.environ.get("WORKSPACE"),"conf.ini")
        config_file = "conf.ini"
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_file))
        ip = config.get("config", "ip")
        username = config.get("config", "username")
        password = config.get("config", "password")
        self.tn = telnetlib.Telnet(ip)
        self.tn.set_debuglevel(2)
        self.tn.read_until('login: ', 5)
        time.sleep(1)
        self.tn.write(username + '\r\n')
        self.tn.read_until('password: ', 5)
        time.sleep(1)
        self.tn.write(password + '\r\n')
        self.tn.read_until('>', 5)
        time.sleep(1)        

    def telnet(self, title, command, keyword, wait_time, error_message, read_until):
        try:
            self.tn.write(command + '\r\n')
            result = self.tn.read_until(read_until, wait_time)
            if "adb" in command and "error" in result:
                self.telnet_only_execute_command("adb kill-server&adb start-server", 5, '>')
                self.tn.write(command + '\r\n')
                result = self.tn.read_until(read_until, wait_time)
            try:
                result = filter(lambda x: keyword in x, result.split("\r\n"))[0].strip()
                if keyword in result:
                    self.nice_print(title + ": " + result)
                else:
                    self.nice_print(error_message) 
                    sys.exit(1)            
            except IndexError:
                self.nice_print(error_message) 
                sys.exit(1)
        except:
            if command != "exit":
                self.__init__()
            self.tn.write(command + '\r\n')
            result = self.tn.read_until(read_until, wait_time)
            if "adb" in command and "error" in result:
                self.telnet_only_execute_command("adb kill-server&adb start-server", 5, '>')
                self.tn.write(command + '\r\n')
                result = self.tn.read_until(read_until, wait_time)
            try:
                result = filter(lambda x: keyword in x, result.split("\r\n"))[0].strip()
                if keyword in result:
                    self.nice_print(title + ": " + result)
                else:
                    self.nice_print(error_message) 
                    sys.exit(1)            
            except IndexError:
                self.nice_print(error_message) 
                sys.exit(1)                        

    def telnet_only_execute_command(self, command, wait_time, read_until):
        try:
            self.tn.write(command + '\r\n')
            result = self.tn.read_until(read_until, wait_time)
            if "adb" in command and "error" in result:
                self.telnet_only_execute_command("adb kill-server&adb start-server", 5, '>')
                self.tn.write(command + '\r\n')
                result = self.tn.read_until(read_until, wait_time)
            return result
        except:
            self.__init__()
            if command != "exit":
                self.tn.write(command + '\r\n')
            result = self.tn.read_until(read_until, wait_time)
            if "adb" in command and "error" in result:
                self.telnet_only_execute_command("adb kill-server&adb start-server", 5, '>')
                self.tn.write(command + '\r\n')
                result = self.tn.read_until(read_until, wait_time)
            return result
        
    def nice_print(self, message, sign='*'):
        print(''.join([' ', sign*len(message)]))
        print(''.join([' ', message]))
        print(''.join([' ', sign*len(message)]))

    def close_telnet(self):
        self.tn.close()

if __name__ == "__main__":
    Telnet = Telnet()
    Telnet.close_telnet()

import jenkinsapi.jenkins as jenkins
import sys
import requests
import time

class handle_jenkins(object):

    def __init__(self,jenkins_server, Username, Password, job_name):
        self.jenkins_server = jenkins_server
        self.Username = Username
        self.Password = Password
        self.job_name = job_name
        #global server
        try:
            self.server = jenkins.Jenkins(self.jenkins_server, username=self.Username, password=self.Password)
            print "jenkins server is connected!"
        except requests.exceptions.ConnectionError:
            info=sys.exc_info()
            print info[0],":",info[1]
            sys.exit(1)

    def get_running_status(self,job, build_number):
        if job.get_build(build_number).is_running():
            return True
        else:
            return False
    def cancel_job(self, job, build_number):
        job.get_build(build_number).stop()

    def build_job(self, server, job_name):
        server.build_job(job_name)

    def main(self,server):        
        for key,job in server.iteritems():
            if key == job_name:
                last_buildnumber = job.get_last_buildnumber()
                if self.get_running_status(job, last_buildnumber) == True:
                    self.cancel_job(job, last_buildnumber)
                    if self.get_running_status(job, last_buildnumber) == False:
                        print "job " + job_name + " is cancelled successfully!"
                        print "start to build again for job " + job_name
                        self.build_job(server,job_name)
                        count = 1
                        while count < 15:
                            try:
                                if self.get_running_status(job, last_buildnumber + 1):
                                    print "job " + job_name + " is started again successfully after " + str(count) + "s!"
                                    break
                            except KeyError:
                                if count == 9:
                                    print "job " + job_name + " is not started after 10s!"
                                    sys.exit(1)
                                time.sleep(1)
                                print str(count) + "s"
                            count += 1
                    else:
                        print "job " + job_name + " is still running, please check!"
                else:
                    print "job " + job_name + " is not running, no need to cancel it!"
                break

if __name__ == "__main__":
    
    jenkins_server = 'http://10.115.101.230:8080/jenkins/'
    Username = "xiaobo.chi"
    Password = "DEVIL_cxb456"
    job_name = "Third_APP_Testing"
    handle_jenkins = handle_jenkins(jenkins_server, Username, Password, job_name)
    handle_jenkins.main(handle_jenkins.server)

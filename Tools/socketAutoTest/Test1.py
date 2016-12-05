import urllib


print urllib.urlopen("http://10.115.101.230:8080/jenkins/view/Monkey/job/UserCare_cn_Monkey/lastSuccessfulBuild/artifact/UserCare.apk").code
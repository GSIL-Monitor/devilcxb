# -*- coding: cp936 -*-
import smtplib  
from email.mime.text import MIMEText  

mailto_list=["xiaobo.chi@tcl.com"]
mail_host="mail.tcl.com"  #���÷�����
mail_user="xinjiu.qiao"    #�û���
mail_pass="zzz25958863/"   #����
mail_postfix="tcl.com"  #������ĺ�׺
  
def send_mail(to_list,sub,content):  
    me="hello"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()
        server.connect(mail_host)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False  
if __name__ == '__main__':  
    if send_mail(mailto_list,"hello","hello world��"):  
        print "���ͳɹ�"  
    else:  
        print "����ʧ��"

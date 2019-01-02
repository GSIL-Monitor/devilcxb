# -*- coding: utf-8 -*-
import sys
import os
import ConfigParser
import datetime


config = ConfigParser.ConfigParser()
# logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "HandleMongoDB"))
from HandleMongoDB import HandleMongoDB
host = config.get("config_mongodb", "host")
port = int(config.get("config_mongodb", "port"))
outsourcing_db = config.get("config_mongodb", "database")
dailyReport_table = config.get("config_mongodb", "table")
HandleMongoDB = HandleMongoDB(host, port)
db_obj = HandleMongoDB.get_db(outsourcing_db)
dailyReport_table_ojb = HandleMongoDB.get_table(db_obj, dailyReport_table)
today = datetime.datetime.now().date()
oneday = datetime.timedelta(days=1)
yestoday = today - oneday
print yestoday
mail_contents = ""
flag = False
for i in HandleMongoDB.query_table(dailyReport_table_ojb, {"date": str(yestoday), "reporter": {"$in": ["任珍", "杨思维", "倪明", "胡惠敏", "吴农中", "曾文繁", "和剑"]}}):
    flag = True
    mail_contents += "Reporter: " + i["reporter"] + "<br/>"
    mail_contents += "TestType: " + i["testType"] + "<br/>"
    if "project" in i.keys():
        if not i["project"]:
            i["project"] = "Others"
        mail_contents += "Project: " + i["project"] + "<br/>"
    if i["testType"] == "ET":
        mail_contents += "ET duration: " + str(i["ET_duration"]) + "<br/>"
        mail_contents += "ET comments: " + "<br/>" + reduce(lambda x, y: x + "<br/>" + y, sorted(i["ET_comments"])) + "<br/>"
        if "ET_bugs" in i.keys():
            mail_contents += "ET bugs: " + "<br/>" + reduce(lambda x, y: x + "<br/>" + y, sorted(i["ET_bugs"])) + "<br/>"
    elif i["testType"] == "self-Learning&Others":
        mail_contents += "self-Learning&Others_comments: " + i["self-Learning&Others_comments"].replace("\n", "<br/>") + "<br/>"
    elif i["testType"] == "Case Execution":
        mail_contents += "caseNumber: " + str(i["caseNumber"]) + "<br/>"
    mail_contents += "<br/><br/>"
if os.path.isfile(os.path.join(os.environ.get("WORKSPACE"), "mail.txt")):
    os.remove(os.path.join(os.environ.get("WORKSPACE"), "mail.txt"))
if flag:
    File = open(os.path.join(os.environ.get("WORKSPACE"), "mail.txt"), "w")
    File.write("mail_content=" + mail_contents.replace("\n", "<br/>").replace("\r", "").encode("utf-8") + "\n")
    File.write("mail_list=" + "cc:xiaobo.chi@tcl.com, cc:zhanyu.huo@tcl.com, liling.wang@tcl.com, zicheng.sun@tcl.com, xixi.qin@tcl.com, tingjie.wang@tcl.com, digao@tcl.com" + "\n")
    # File.write("mail_list=" + "xiaobo.chi@tcl.com," + "\n")
    File.write("mail_subject=Daily Report_" + str(yestoday))
    File.close()
    HandleMongoDB.close_mongodb()
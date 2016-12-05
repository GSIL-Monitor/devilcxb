# -*- coding: utf-8 -*-
import os
import ConfigParser
import logging
import datetime
import sys
import chardet
import re
logging.basicConfig(level=logging.INFO)


class DailyReport(object):
    def __init__(self):
        pass

    def GetJenkinsVar(self, key):
        """
        获取构建jenkins job时的参数值
        :param key: 参数名称
        :return: 参数值
        """
        try:
            value = os.environ.get(key)
        except Exception:
            value = os.environ.get(key.upper())
        #print('value = ',value)
        if(not value):
            value = ''
        #print( os.path.join(r'c:/a',value) )
        return value

    def main(self):
        dailyReport = {}
        reporter = self.GetJenkinsVar("Name").decode("gb2312").encode("utf-8")
        dailyReport["reporter"] = reporter
        logging.info("reporter: " + self.GetJenkinsVar("Name"))
        testType = self.GetJenkinsVar("testType")
        dailyReport["testType"] = testType
        logging.info("Test Type: " + testType)
        project_flag = False
        if testType == "ET":
            project_flag = True
            ET_duration = self.GetJenkinsVar("ET_duration")
            if not ET_duration:
                logging.error("ET duration is not filled!")
                sys.exit(1)
            dailyReport["ET_duration"] = float(ET_duration)
            logging.info("ET Duration: " + ET_duration)
            ET_comments = self.GetJenkinsVar("ET_comments")
            if ET_comments:
                dailyReport["ET_comments"] = filter(lambda x: x, list(set(ET_comments.decode("gb2312").encode("utf-8").split("\n"))))
                for ET_comment in dailyReport["ET_comments"]:
                    logging.info("ET Comments: " + ET_comment.decode("utf-8").encode("gb2312"))
            else:
                logging.error("ET comments is not filled!")
                sys.exit(1)
            ET_bugs = self.GetJenkinsVar("ET_bugs")
            if ET_bugs:
                dailyReport["ET_bugs"] = filter(lambda x: re.match("http://jira.lab.tclclouds.com/.*", x), ET_bugs.split("\n"))
                if not dailyReport["ET_bugs"]:
                    logging.warning("ET bugs is not filled correctly!")
                else:
                    for ET_bug in dailyReport["ET_bugs"]:
                        logging.info("ET_bug: " + ET_bug)
        elif testType == "Case Execution":
            project_flag = True
            if not self.GetJenkinsVar("caseNumber"):
                logging.error("caseNumber is not filled!")
                sys.exit(1)
            caseNumber = int(self.GetJenkinsVar("caseNumber"))
            dailyReport["caseNumber"] = caseNumber
            logging.info("Number of Case Execution: " + str(caseNumber))
        elif testType == "self-Learning&Others":
            dailyReport["self-Learning&Others_comments"] = self.GetJenkinsVar("self-Learning&Others_comments").decode("gb2312").encode("utf-8")
            logging.info("self-Learning&Others_comments: " + self.GetJenkinsVar("self-Learning&Others_comments"))
        if project_flag:
            test_project = self.GetJenkinsVar("project")
            dailyReport["project"] = test_project
            logging.info("project: " + test_project)
        else:
            dailyReport["project"] = None
        caseReviewIssue = self.GetJenkinsVar("caseReviewIssue").decode("gb2312").encode("utf-8")
        caseReviewIssueResult = {}
        if caseReviewIssue:
            try:
                caseReviewIssueResult["case_executor"] = re.findall(".*:|：(.*)", caseReviewIssue.split("\n")[0])[0]
            except IndexError:
                caseReviewIssueResult["case_executor"] = caseReviewIssue.split("\n")[0]
            logging.info("Review comments for the executor of: " + caseReviewIssueResult["case_executor"].decode("utf-8").encode("gb2312"))
            issue_count = 1
            for issue in caseReviewIssue.split("\n")[1:]:
                caseReviewIssueResult["issue" + str(issue_count)] = issue.strip()
                logging.info("issue" + str(issue_count) + ": " + issue.strip().decode("utf-8").encode("gb2312"))
                issue_count += 1
            dailyReport["caseReviewResult"] = caseReviewIssueResult
            # logging.info("Case Review Result: " + str(caseReviewIssueResult))
        date = str(datetime.datetime.now().date())
        dailyReport["date"] = date
        logging.info("Date: " + str(date))
        config = ConfigParser.ConfigParser()
        # logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        sys.path.append(os.path.join(self.GetJenkinsVar("WORKSPACE"), "HandleMongoDB"))
        from HandleMongoDB import HandleMongoDB
        host = config.get("config_mongodb", "host")
        port = int(config.get("config_mongodb", "port"))
        outsourcing_db = config.get("config_mongodb", "database")
        dailyReport_table = config.get("config_mongodb", "table")
        HandleMongoDB = HandleMongoDB(host, port)
        db_obj = HandleMongoDB.get_db(outsourcing_db)
        dailyReport_table_ojb = HandleMongoDB.get_table(db_obj, dailyReport_table)
        if HandleMongoDB.query_table(dailyReport_table_ojb, {"reporter": dailyReport["reporter"], "project": dailyReport["project"], "testType": dailyReport["testType"], "date": dailyReport["date"]}):
            HandleMongoDB.update_item(dailyReport_table_ojb, {"reporter": dailyReport["reporter"], "project": dailyReport["project"], "testType": dailyReport["testType"], "date": dailyReport["date"]}, dailyReport)
            logging.warning("already reported, but still update it again!")
        else:
            HandleMongoDB.insert_item(dailyReport_table_ojb, dailyReport)
            logging.info("Daily Report is generated finished!")


if __name__ == '__main__':
    DailyReport = DailyReport()
    DailyReport.main()




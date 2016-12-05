# -*- coding: utf-8 -*-
import os
import ConfigParser
import logging
import datetime
import sys
import chardet
import urllib2
import urllib
import re
import datetime
logging.basicConfig(level=logging.INFO)


class KPI(object):
    def __init__(self):
        """
        init KPI and connection to MongoDB
        Returns: None

        """
        config = ConfigParser.ConfigParser()
        # logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        # sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "HandleMongoDB"))
        from HandleMongoDB import HandleMongoDB
        host = config.get("config_mongodb", "host")
        port = int(config.get("config_mongodb", "port"))
        outsourcing_db = config.get("config_mongodb", "database")
        dailyReport_table = config.get("config_mongodb", "table")
        backlog_table = config.get("config_mongodb", "table_backlog")
        self.HandleMongoDB = HandleMongoDB(host, port)
        db_obj = self.HandleMongoDB.get_db(outsourcing_db)
        self.table_obj = self.HandleMongoDB.get_table(db_obj, dailyReport_table)
        self.backlog_table_obj = self.HandleMongoDB.get_table(db_obj, backlog_table)
        selfInfo_table = config.get("config_mongodb", "table_selfInfo")
        self.selfInfo_table_obj = self.HandleMongoDB.get_table(db_obj, selfInfo_table)
        kpi_table = config.get("config_mongodb", "table_kpi")
        self.kpi_table_obj = self.HandleMongoDB.get_table(db_obj, kpi_table)
        self.start_date, self.end_date = self.GetCurrentMonthDay()
        # sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "HandleJira"))
        from HandleJira import HandleJira
        jira_server = config.get("config_jira", "server")
        self.jira_username = config.get("config_jira", "username")
        self.jira_password = config.get("config_jira", "password")
        self.HandleJira = HandleJira(jira_server, self.jira_username, self.jira_password)

    def get_reporter(self):
        """
        Get Reporter
        Returns: Reporter

        """
        return filter(lambda x: x, list(set(map(lambda x: x["reporter"], self.HandleMongoDB.query_table(self.table_obj, {"date": {"$gte": self.start_date, "$lte": self.end_date}}, {"reporter": 1})))))

    def GetCurrentMonthDay(currentday):
        """
        Get start date and end date
        Returns:

        """
        currentMonth = datetime.datetime.now().strftime('%m')
        currentYear = datetime.datetime.now().strftime('%Y')
        d1 = datetime.datetime(int(currentYear),int(currentMonth) - 1,1)
        d2 = datetime.datetime(int(currentYear),int(currentMonth),1)
        days = d2 - d1
        day = days.days
        return str(datetime.date(int(currentYear),int(currentMonth) - 1,1).strftime("%Y-%m-%d")),\
               str(datetime.date(int(currentYear),int(currentMonth) - 1,day).strftime("%Y-%m-%d"))

    def get_et_comments_number(self, reporter):
        """
        get comments number of ET
        Args:
            reporter: reporter

        Returns: number of ET comments from the reporter

        """
        et_comments = self.HandleMongoDB.query_table(self.table_obj, {"reporter": reporter, "ET_comments": {"$exists": True}, "date": {"$gte": self.start_date, "$lte": self.end_date}}, {"ET_comments": 1})
        if et_comments:
            et_comments_number = sum(map(lambda x: len(x["ET_comments"]), et_comments))
            return et_comments_number
        else:
            return 0

    def get_case_execution_number(self, reporter):
        case_execution_number = self.HandleMongoDB.query_table(self.table_obj, {"reporter": reporter, "caseNumber": {"$exists": True}, "date": {"$gte": self.start_date, "$lte": self.end_date}}, {"caseNumber": 1})
        if case_execution_number:
            case_execution_number = sum(map(lambda x: x["caseNumber"], case_execution_number))
            return case_execution_number
        else:
            return 0


    def get_positive_And_nagative(self, reporter):
        """
        Get positive and nagative number
        Args:
            reporter: reporter

        Returns: number of positive and nagative

        """
        positive_number = len(self.HandleMongoDB.query_table(self.backlog_table_obj, {"Name": reporter, "Date": {"$gte": self.start_date, "$lte": self.end_date}, "Positive": True}))
        nagative_number = len(self.HandleMongoDB.query_table(self.backlog_table_obj, {"Name": reporter, "Date": {"$gte": self.start_date, "$lte": self.end_date}, "Positive": False}))
        return positive_number - nagative_number

    def get_caseReview_comments(self, reporter):
        """
        Get review comments from Reporter
        Args:
            reporter: reporter

        Returns: review comments

        """
        caseReviewComments = self.HandleMongoDB.query_table(self.table_obj, {"reporter": reporter, "date": {"$gte": self.start_date, "$lte": self.end_date}, "caseReviewResult": {"$exists": True}})
        if caseReviewComments:
            print len(map(lambda x: x["caseReviewResult"], caseReviewComments))
            return map(lambda x: x["caseReviewResult"], caseReviewComments)
        else:
            return []

    def close_mongo(self):
        """
        close the connection from MongoDb
        Returns: None

        """
        self.HandleMongoDB.close_mongodb()

    def get_issues(self, reporter, priority_list):
        """
        获取bug
        Args:
            reporter: bug reporter
            priority_list: 优先级列表

        Returns: bug数量

        """
        # return 30
        return len(self.HandleJira.filter_issue(reporter, self.start_date, self.end_date, priority_list))

    def get_jira_account(self, reporter):
        """
        获取jira的账号
        Args:
            reporter: 填日报人

        Returns: jira账号

        """
        return self.HandleMongoDB.query_table(self.selfInfo_table_obj, {"Name": reporter}, {"jira_account": 1})[0]["jira_account"]

    def get_refused_issues(self, reporter):
        """
        获取被拒绝bug的数量
        Args:
            reporter: 报bug的作者

        Returns:被拒绝bug的数量

        """
        # return 0
        count = 0
        refused_issues = self.HandleJira.filter_issue(reporter, refused_start_date=self.start_date, refused_end_date=self.end_date, status_list=["Closed", "Refused"], refused_reason_list=["拒绝_bug描述不清晰", "拒绝_产品确认不修改", "拒绝_测试操作错误", "拒绝_重复bug", "拒绝_需求理解错误"])
        for refuse_issue in refused_issues:
            if self.check_refused_real(refuse_issue):
                count += 1
        return count

    def check_refused_real(self, issue_obj):
        """
        check if issue is refused really
        Args:
            issue_obj: issue object

        Returns: True/False

        """
        data = {"os_username": self.jira_username, "os_password": self.jira_password}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"}
        url = issue_obj.permalink() + "?page=com.atlassian.jira.plugin.system.issuetabpanels:changehistory-tabpanel"
        req = urllib2.Request(url, data=urllib.urlencode(data), headers=headers)
        contents = urllib2.urlopen(req).read().replace("\n", "")
        # contents = reduce(lambda x, y: x.strip + y.strip(), contents)
        status_history =filter(lambda x: x in ["Accept/Processing", "Solved", "New", "Closed", "Refused", "Reopened", "Suspended"], map(lambda x: x[:-1].strip(), re.findall('class="activity-new-val">(.*?<)', contents)))
        if status_history[-2:] != ["Refused", "Closed"] and status_history[-1] != "Refused":
            logging.warning( url + " is not a real refused issue!")
            return False
        else:
            return True

    def get_rate(self, value_list):
        """
        获取比率
        Args:
            value_list:值列表

        Returns:

        """
        if max(value_list) != 0:
            return float(format(float(100)/float(max(value_list)), ".2f"))
        else:
            if min(value_list) == 0:
                return 0
            else:
                return float(format(float(100)/float(min(value_list)), ".2f"))

    def get_score1(self, current_value, value_list, rate, return_zero=False, return_rate=True, flag=False):
        if current_value == 0 and return_zero:
            return 0
        minus_flag = False
        if abs(current_value) != current_value:
            minus_flag = True
            current_value = abs(current_value)
        if minus_flag:
            value_list = map(lambda x: abs(x), filter(lambda x: x <= 0, value_list))
        max_value = max(value_list)
        if max_value == 0:
            if return_rate:
                return rate
            else:
                return 0
        if minus_flag:
            return -rate*(1 - float(format((float(max_value - current_value)*0.3)/max_value, ".2f")))
        return rate*(1 - float(format((float(max_value - current_value)*0.3)/max_value, ".2f")))

    def get_score(self, current_value, value_list, rate):
        wight1 = rate  #权重
        actualCountMax1 = max(value_list) #单项最大计数，
        actualCountMin1 = min(value_list) #单项最小计数，得分最少的人
        if actualCountMax1 == actualCountMin1:
            return wight1*0.7
        actual_a = current_value #某人单项原始计数，肯定在单项最小计数和最大计数之间

        scorePerWight = float(100-70)/wight1 #过程，可忽略
        actualCountPerWight = float(actualCountMax1 - actualCountMin1)/wight1 #过程，可忽略
        #得到某人单项分数，在60~100之间。
        score_1_a = float(100-70)/(actualCountMax1 - actualCountMin1)*(actual_a-actualCountMin1) + 70
        #得到映射到权重下的分数
        score_1_a_scale = score_1_a/100*wight1
        return score_1_a_scale

    def main(self):
        details = {}
        details_from_space_cleaner = {u"杨思维":{"Case_Execution_Number": float(201), "issue_above&eaque_normal": float(121)*0.3, "issue_under_normal": float(121)*0.7}, u"蒲杨洋": {"Case_Execution_Number": float(241), "issue_above&eaque_normal": float(117)*0.3, "issue_under_normal": float(117)*0.7}, u"王果": {"Case_Execution_Number": float(180), "issue_above&eaque_normal": float(120)*0.3, "issue_under_normal": float(120)*0.7}, u"曾文繁": {"Case_Execution_Number": float(259), "issue_above&eaque_normal": float(1136)*0.3, "issue_under_normal": float(136)*0.7}, u"倪明": {"Case_Execution_Number": float(182), "issue_above&eaque_normal": float(131)*0.3, "issue_under_normal": float(131)*0.7}}
        for reporter in self.get_reporter():
            logging.info("Reporter: " +  reporter)
            logging.info("ET comments number: " + str( self.get_et_comments_number(reporter)))
            if reporter not in details.keys():
                details[reporter] = {"ET_Comments_Number": self.get_et_comments_number(reporter)}
            else:
                details[reporter]["ET_Comments_Number"] = self.get_et_comments_number(reporter)
            logging.info("Case execution number: " + str( self.get_case_execution_number(reporter)))
            details[reporter]["Case_Execution_Number"] = self.get_case_execution_number(reporter)
            positive_and_nagative_number = self.get_positive_And_nagative(reporter)
            logging.info("Number of positive and nagative: " + str(positive_and_nagative_number))
            details[reporter]["Positive&Nagative_Number"] = positive_and_nagative_number
            review_comments_flag = False
            for caseReviewComment in self.get_caseReview_comments(reporter):
                case_executer = caseReviewComment["case_executor"]
                if case_executer not in self.get_reporter():
                    details[reporter]["Positive&Nagative_Number"] = details[reporter]["Positive&Nagative_Number"] - 1
                    logging.warning("wrong daily report filled, since Review Comments is reported as a wrong format!")
                    break
                review_comments_flag = True
                reviewComments_number = len(caseReviewComment.keys()) - 1
                if "reviewComments_number" not in details[reporter].keys():
                    details[reporter]["reviewComments_number"] = reviewComments_number
                else:
                    details[reporter]["reviewComments_number"] = details[reporter]["reviewComments_number"] + reviewComments_number
                if case_executer not in details.keys():
                    details[case_executer] = {"reviewComments_from_others_number": reviewComments_number}
                else:
                    if "reviewComments_from_others_number" not in details[case_executer].keys():
                        details[case_executer]["reviewComments_from_others_number"] = reviewComments_number
                    else:
                        details[case_executer]["reviewComments_from_others_number"] = details[case_executer]["reviewComments_from_others_number"] + reviewComments_number
            if review_comments_flag:
                logging.info("review comments Number: " + str(details[reporter]["reviewComments_number"]))
            logging.info("Jira Account: " + self.get_jira_account(reporter))
            jira_account = self.get_jira_account(reporter).encode("utf-8")
            issue_aboveAndeaque_normal_number = self.get_issues(jira_account, ["严重", "致命", "一般"])
            details[reporter]["issue_above&eaque_normal"] = issue_aboveAndeaque_normal_number
            logging.info("Number of issues that above and eaque to Normal: " + str(issue_aboveAndeaque_normal_number))
            issue_under_normal_number = self.get_issues(jira_account, ["提示", "建议"])
            details[reporter]["issue_under_normal"] = issue_under_normal_number
            logging.info("Number of issues that under of Normal: " + str(issue_under_normal_number))
            issue_refusedl_number = self.get_refused_issues(jira_account)
            details[reporter]["issue_refused"] = issue_refusedl_number
            logging.info("Number of issues that is refused: " + str(issue_refusedl_number))
        max_case_number = max(map(lambda x: details[x]["Case_Execution_Number"], details))
        max_case_number_space_cleaner = max(map(lambda x: details_from_space_cleaner[x]["Case_Execution_Number"], details_from_space_cleaner))
        max_issue_above_eaque_normal = max(map(lambda x: details[x]["issue_above&eaque_normal"], details))
        max_issue_above_eaque_normal_space_cleaner = max(map(lambda x: details_from_space_cleaner[x]["issue_above&eaque_normal"], details_from_space_cleaner))
        max_issue_under_normal = max(map(lambda x: details[x]["issue_under_normal"], details))
        max_issue_under_normal_space_cleaner = max(map(lambda x: details_from_space_cleaner[x]["issue_under_normal"], details_from_space_cleaner))
        for reporter in details_from_space_cleaner.keys():
            details_from_space_cleaner[reporter]["Case_Execution_Number"] = float(max_case_number)/float(max_case_number_space_cleaner)*details_from_space_cleaner[reporter]["Case_Execution_Number"]
            details_from_space_cleaner[reporter]["issue_above&eaque_normal"] = float(max_issue_above_eaque_normal)/float(max_issue_above_eaque_normal_space_cleaner)*details_from_space_cleaner[reporter]["issue_above&eaque_normal"]
            details_from_space_cleaner[reporter]["issue_under_normal"] = float(max_issue_under_normal)/float(max_issue_under_normal_space_cleaner)*details_from_space_cleaner[reporter]["issue_under_normal"]
        for reporter in details.keys():
            if "reviewComments_from_others_number" not in details[reporter].keys():
                details[reporter]["reviewComments_from_others_number"] = 0
            if "reviewComments_number" not in details[reporter].keys():
                details[reporter]["reviewComments_number"] = 0
            if reporter in details_from_space_cleaner.keys():
                details[reporter]["Case_Execution_Number"] = details_from_space_cleaner[reporter]["Case_Execution_Number"]
                details[reporter]["Case_Execution_Score"] = self.get_score(details_from_space_cleaner[reporter]["Case_Execution_Number"], map(lambda x: details_from_space_cleaner[x]["Case_Execution_Number"], details_from_space_cleaner.keys()), 25)
            else:
                details[reporter]["Case_Execution_Score"] = self.get_score(details[reporter]["Case_Execution_Number"], map(lambda x: details[x]["Case_Execution_Number"], details.keys()), 25)

            if reporter in details_from_space_cleaner.keys():
                details[reporter]["issue_above&eaque_normal"] = details_from_space_cleaner[reporter]["issue_above&eaque_normal"]
                details[reporter]["issue_under_normal"] = details_from_space_cleaner[reporter]["issue_under_normal"]
                details[reporter]["issue_above&eaque_normal_score"] = self.get_score(details_from_space_cleaner[reporter]["issue_above&eaque_normal"], map(lambda x: details_from_space_cleaner[x]["issue_above&eaque_normal"], details_from_space_cleaner.keys()), 15)
                details[reporter]["issue_under_normal_score"] = self.get_score(details_from_space_cleaner[reporter]["issue_under_normal"], map(lambda x: details_from_space_cleaner[x]["issue_under_normal"], details_from_space_cleaner.keys()), 10)
            else:
                details[reporter]["issue_above&eaque_normal_score"] = self.get_score(details[reporter]["issue_above&eaque_normal"], map(lambda x: details[x]["issue_above&eaque_normal"], details.keys()), 15)
                details[reporter]["issue_under_normal_score"] = self.get_score(details[reporter]["issue_under_normal"], map(lambda x: details[x]["issue_under_normal"], details.keys()), 10)
            if reporter not in details_from_space_cleaner.keys():
                details[reporter]["ET_Comments_Score"] = self.get_score(details[reporter]["ET_Comments_Number"], map(lambda x: details[x]["ET_Comments_Number"], details.keys()), 15)
            else:
                details[reporter]["ET_Comments_Score"] = 15*0.7
            details[reporter]["Positive&Nagative_Score"] = self.get_score(details[reporter]["Positive&Nagative_Number"], map(lambda x: details[x]["Positive&Nagative_Number"], details.keys()), 15)
            # details[reporter]["issue_refused_Score"] = 20 - self.get_score(details[reporter]["issue_refused"], map(lambda x: details[x]["issue_refused"], details.keys()), 20, return_zero=True)
            details[reporter]["issue_refused_Score"] = 20*0.7
            mark = details[reporter]["Case_Execution_Score"] + details[reporter]["issue_above&eaque_normal_score"] + details[reporter]["issue_under_normal_score"] + details[reporter]["ET_Comments_Score"] + details[reporter]["Positive&Nagative_Score"] + details[reporter]["issue_refused_Score"]
            details[reporter]["mark"] = mark
            details[reporter]["Name"] = reporter
            details[reporter]["date"] = str(datetime.datetime.now().strftime("%Y-%m-%d"))
            print reporter
            print details[reporter]["Case_Execution_Score"]
            print details[reporter]["issue_above&eaque_normal_score"] + details[reporter]["issue_under_normal_score"] + details[reporter]["issue_refused_Score"]
            # print details[reporter]["issue_under_normal_score"]
            print details[reporter]["ET_Comments_Score"]
            print details[reporter]["Positive&Nagative_Score"]
            # print details[reporter]["issue_refused_Score"]
            print mark
            self.HandleMongoDB.insert_item(self.kpi_table_obj, details[reporter])
        self.close_mongo()

if __name__ == '__main__':
    KPI = KPI()
    KPI.main()

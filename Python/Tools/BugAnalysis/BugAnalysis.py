# -*- coding:utf-8 -*-
from Tools.Common.TelnetHandle.TelnetHandle import TelnetHandle
import logging
import re
import datetime
import calendar
import collections

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class BugAnalysis(object):
    def __init__(self, product_id='29', month=9, start_date=None, end_date=None, year=2018):
        """
        1. 首先要提供开发人员，把web前端，IOS，Android的开发人员分开到对应的权限分组里面。
        2. 找到对应的项目ID，如真量对应的ID为29。
        3. 定义月份，如9月，或者起止日期。
        """
        self.product_id = product_id
        self.zentao_host = {"host": "10.40.11.129", "port": "22", "username": "root",
                            "password": "@6ePB#ms@)!&yooli!@!^",
                            "db_login_command": "/opt/zbox/bin/mysql -u root -P 3307 -p123456 zentao"}
        if start_date:
            first_day, last_day = start_date, end_date
        else:
            first_day, last_day = self.getMonthFirstDayAndLastDay(year=year, month=month)
        first_day = first_day + " 00:00:00"
        last_day = last_day + " 23:59:59"
        self.tn = TelnetHandle("10.40.10.78", "root", "@6ePB#ms@)!&yooli!@!^")
        self.valid_bug_sql_query = "select id, title, severity, openedBy, resolvedBy, openedDate, status from zt_bug where openedDate >= '%s' and openedDate <= '%s' and product='%s' and resolvedBy in (SELECT account FROM `zt_usergroup` WHERE `group` in ('2', '4', '5', '6', '7', '13', '14', '15')) and resolution not in ('bydesign', 'duplicate', 'notrepro', 'willnotfix', 'automation') and deleted = '0';" % (
            first_day, last_day, self.product_id)
        logging.info(self.valid_bug_sql_query)
        self.online_bug_sql_query = "select id, title, severity, openedBy, resolvedBy, openedDate, status from zt_bug where openedDate >= '%s' and openedDate <= '%s' and product='%s' and (title like '%%线上问题%%' or title like '%%上线过程问题%%') and deleted = '0';" % (
            first_day, last_day, self.product_id)
        logging.info(self.online_bug_sql_query)
        self.online_bug_all_sql_query = "select id, title, severity, openedBy, resolvedBy, openedDate, status from zt_bug where product='%s' and (title like '%%线上问题%%' or title like '%%上线过程问题%%') and deleted = '0';" % self.product_id
        logging.info(self.online_bug_all_sql_query)
        # first_day = "2018-09-22"
        self.online_comments_query = "select objectID, REPLACE(REPLACE(comment, CHAR(10), ''), CHAR(13), '') as comment from zt_action where date >= '%s' and date <= '%s' and action in ('closed', 'commented', 'edited', 'resolved') and objectType='bug' and comment like '%%测试环境是否存在%%' and product=',%s,';" % (
            first_day, last_day, self.product_id)
        logging.info(self.online_comments_query)
        self.user_group_query = "select zt_group.name, zt_usergroup.account from zt_usergroup, zt_group where zt_group.id in ('2', '4', '5', '6', '7', '13', '14', '15') and zt_group.id=zt_usergroup.group;"
        self.normal_relased_query = "select count(1) from zt_release where zt_release.date>= '%s' and zt_release.date <= '%s'  and zt_release.desc not like '%%插入%%' and product='%s';" % (
            first_day, last_day, self.product_id)
        logging.info(self.normal_relased_query)
        # 延期的版本判断条件： 已zt_release表中的标题和发布时间作为比较，如果发布时间比标题晚，则视为延期发布。
        self.delay_released_query = "select count(1) from zt_release where zt_release.date>= '%s' and zt_release.date <= '%s' and REPLACE(zt_release.date, '-', '') > zt_release.name and product='%s';" % (
            first_day, last_day, self.product_id)
        logging.info(self.delay_released_query)
        # 插入需要会在zt_release表里面的desc字段查询相对日期范围内是否有插入的标记
        self.insert_relased_query = "select count(1) from zt_release where zt_release.date>= '%s' and zt_release.date <= '%s'  and zt_release.desc like '%%插入%%' and product='%s';" % (
            first_day, last_day, self.product_id)
        logging.info(self.insert_relased_query)
        # 发布的需求会在zt_release表里面查询相对日期范围内的stoires字段
        self.released_stories_query = "select REPLACE(group_concat(stories), ',,', ',') from zt_release where zt_release.date>= '%s' and zt_release.date <= '%s' and product='%s';" % (
            first_day, last_day, self.product_id)
        logging.info(self.released_stories_query)
        # P0通过用例的逻辑：查询相对时间范围内优先级为1的用例执行通过数量
        self.p0_passed_query = "select count(1) from zt_testresult result, zt_case test_case where result.date>='%s' and result.date<='%s' and result.case=test_case .id and test_case .product='%s' and test_case .pri=1 and result.caseResult='pass';" % (
            first_day, last_day, self.product_id)
        logging.info(self.p0_passed_query)
        # P0通过用例的逻辑：查询相对时间范围内优先级为1的用例执行失败数量
        self.p0_failed_query = "select count(1) from zt_testresult result, zt_case test_case where result.date>='%s' and result.date<='%s' and result.case=test_case .id and test_case .product='%s' and test_case .pri=1 and result.caseResult='fail';" % (
            first_day, last_day, self.product_id)
        logging.info(self.p0_failed_query)
        # 查询相对时间范围内的插入需求
        self.insert_stories_query = "select group_concat(title separator '&&') from zt_story where id in (%s) and title like '%%插入需求%%';"
        self.changed_stories_query = "select count(1) from zt_story where version>1"
        self.tn.exe_cmd("ssh %s@%s" % (self.zentao_host["username"], self.zentao_host["host"]), "password: ", 15)
        self.tn.exe_cmd(self.zentao_host["password"], "# ")
        self.tn.exe_cmd(self.zentao_host["db_login_command"], "[zentao]> ")

    def getMonthFirstDayAndLastDay(self, year=None, month=None):
        """
        :param year: 年份，默认是本年，可传int或str类型
        :param month: 月份，默认是本月，可传int或str类型
        :return: firstDay: 当月的第一天，datetime.date类型
                  lastDay: 当月的最后一天，datetime.date类型
        """
        if year:
            year = int(year)
        else:
            year = datetime.date.today().year

        if month:
            month = int(month)
        else:
            month = datetime.date.today().month

        # 获取当月第一天的星期和当月的总天数
        firstDayWeekDay, monthRange = calendar.monthrange(year, month)

        # 获取当月的第一天
        firstDay = datetime.date(year=year, month=month, day=1)
        lastDay = datetime.date(year=year, month=month, day=monthRange)

        return firstDay, lastDay

    def get_users(self):
        """

        :return:
        """
        users = filter(lambda x: re.match("\| (.*) +\| (.*) +\|", x),
                       self.tn.exe_cmd(self.user_group_query, "[zentao]> ").split("\r\n"))[1:]
        users = map(lambda x: re.match("\| (.*) +\| (.*) +\|", x).groups(), users)
        users_dict = {}
        for user in users:
            print user
            group_name = user[0].strip()
            user = user[1].strip()
            if group_name not in users_dict.keys():
                users_dict[group_name] = [user]
            else:
                users_dict[group_name].append(user)
        return users_dict

    def get_valid_bugs(self):
        """

        :return:
        """
        return self.get_bugs(self.valid_bug_sql_query)

    def get_online_bugs(self):
        """

        :return:
        """
        return self.get_bugs(self.online_bug_sql_query)

    def get_online_bugs_all(self):
        """

        :return:
        """
        return self.get_bugs(self.online_bug_all_sql_query)

    def get_bugs(self, query):
        """

        :return:
        """
        valid_bugs = filter(
            lambda x: re.match("\| +(\d+) \| (.*)? +\| +(\d) \| (.*)? +\| (.*)? +\| (.*)? +\| (.*)? +\|",
                               x),
            self.tn.exe_cmd(query, "[zentao]> ").split("\r\n"))
        valid_bug_dict = {}
        for valid_bug in valid_bugs:
            print valid_bug
            valid_bug = re.match("\| +(\d+) \| (.*)? +\| +(\d) \| (.*)? +\| (.*)? +\| (.*)? +\| (.*)? +\|",
                                 valid_bug).groups()
            temp_dict = {"title": valid_bug[1].strip(),
                         "severity": valid_bug[2].strip(), "created_by": valid_bug[3].strip(),
                         "fixed_by": valid_bug[4].strip(), "opened_date": valid_bug[5].strip(),
                         "status": valid_bug[6].strip()}
            valid_bug_dict[valid_bug[0].strip()] = temp_dict
        return valid_bug_dict

    def get_online_comments(self):
        """

        :return:
        """
        online_comments = filter(lambda x: re.match(
            "\| +(\d+) \|.*?测试环境是否存在：(.*?<).*?根源：(.*?<).*?后期优化：(.*?<).*?修复方式：(.*?<).*?>修改逻辑：(.*?<)",
            x.replace("&nbsp;", "").replace("<span>", "")),
                                 self.tn.exe_cmd(self.online_comments_query, "[zentao]> ").split("\r\n"))
        online_comments_dict = {}
        for online_comment in online_comments:
            print online_comment
            online_comment = re.match(
                "\| +(\d+) \|.*?测试环境是否存在：(.*?<).*?根源：(.*?<).*?后期优化：(.*?<).*?修复方式：(.*?<).*?>修改逻辑：(.*?<)",
                online_comment.replace("&nbsp;", "").replace("<span>", "")).groups()
            temp_dict = {"existed_qa_env": online_comment[1].strip()[:-1], "root_cause": online_comment[2].strip()[:-1],
                         "optimized_from_qa": online_comment[3].strip()[:-1],
                         "handle_way": online_comment[4].strip()[:-1],
                         "fixed_plan": online_comment[5].strip()[:-1]}
            online_comments_dict[online_comment[0]] = temp_dict
        return online_comments_dict

    def get_query_count(self, sql_query):
        cmd_result = self.tn.exe_cmd(sql_query, "[zentao]> ").split("\r\n")
        query_result = filter(lambda x: re.match("\| +(\d+) \|", x),
                              cmd_result)
        if query_result:
            query_result = query_result[0]
            return re.match("\| +(\d+) \|", query_result).groups()[0]
        logging.warning(cmd_result)
        return

    def get_released_stories(self):
        cmd_result = self.tn.exe_cmd(self.released_stories_query, "[zentao]> ").split(
            "\r\n")
        query_result = filter(lambda x: re.match("\|[ ,]+(\d+.*\d+).*\|", x),
                              cmd_result)
        if query_result:
            query_result = query_result[0]
            return re.match("\|[ ,]+(\d+.*\d+).*\|", query_result).groups()[0]
        logging.warning(cmd_result)
        return

    def get_inserted_stories(self, inserted_stories_query):
        cmd_result = self.tn.exe_cmd(inserted_stories_query, "[zentao]> ").split(
            "\r\n")
        query_result = filter(lambda x: re.match("\|[ ,]+(.*&&.*).*\|", x),
                              cmd_result)
        if len(query_result) > 1:
            query_result = query_result[-1]
            return query_result.replace(" ", "").replace("|", "").split("&&")
        logging.warning(cmd_result)
        return

    def post_action(self):
        """

        :return:
        """
        self.tn.exe_cmd("exit", "# ")
        self.tn.exe_cmd("exit", "$ ")
        self.tn.close_telnet()

    def main(self):
        """

        :return:
        """
        users = self.get_users()
        online_comments = self.get_online_comments()
        valid_bugs = self.get_valid_bugs()
        online_bugs = self.get_online_bugs()
        online_bugs_all = self.get_online_bugs_all()
        delay_release_count = self.get_query_count(self.delay_released_query)
        normal_release_count = self.get_query_count(self.normal_relased_query)
        insert_release_count = self.get_query_count(self.insert_relased_query)
        released_stories = self.get_released_stories()
        if released_stories:
            released_stories = released_stories.replace(",,", ",")
            logging.info(self.insert_stories_query % (released_stories))
            insert_stories = self.get_inserted_stories(self.insert_stories_query % (released_stories))
        changed_stories_count = self.get_query_count(self.changed_stories_query + " and id in (%s);" % released_stories)
        p0_passed_count = self.get_query_count(self.p0_passed_query)
        p0_failed_count = self.get_query_count(self.p0_failed_query)
        self.post_action()
        # print online_bugs
        print "#######################################start to analyze######################################"
        print online_comments
        if online_comments:
            for bug_id in online_comments:
                # print "%s: " % bug_id
                print "%s\t" % online_bugs_all[bug_id]["title"],
                print "%s\t" % online_bugs_all[bug_id]["created_by"],
                print "%s\t" % online_comments[bug_id]["existed_qa_env"],
                print "%s\t" % online_comments[bug_id]["root_cause"],
                print "%s\t" % online_comments[bug_id]["optimized_from_qa"],
                print "%s\t" % online_comments[bug_id]["handle_way"],
                print "%s\t" % online_comments[bug_id]["fixed_plan"]
                # for key in online_comments[bug_id].keys():
                #     print "%s: %s" % (key, online_comments[bug_id][key])
            # 20181105: 增加线上问题测试环境是否存在的分析。
            existed_qa_env_dict = collections.Counter(map(lambda x: x["existed_qa_env"], online_comments.values()))
            print "测试环境是否存在分析："
            for existed_qa_env in existed_qa_env_dict:
                print "\t%s: %s" % (existed_qa_env, existed_qa_env_dict[existed_qa_env])
            handle_way_dict = collections.Counter(map(lambda x: x["handle_way"], online_comments.values()))
            print "修复方式："
            for handle_way in handle_way_dict:
                print "\t%s: %s" % (handle_way, handle_way_dict[handle_way])
        else:
            logging.warning("no online bugs is available!")

        if valid_bugs:
            print "amount of bugs: %s" % len(valid_bugs.keys())
            for group in users:
                print group
                severity_list = []
                for bug_id in valid_bugs:
                    if valid_bugs[bug_id]["fixed_by"] in users[group]:
                        # 20181105: 新增打印产品经理bug， 便于分析。
                        if group == '产品经理':
                            print "\t%s: %s" % (bug_id, valid_bugs[bug_id]["title"])
                        severity_list.append(valid_bugs[bug_id]["severity"])
                print "\t%s: %s" % (group, len(severity_list))
                severity_dict = collections.Counter(severity_list).most_common()
                for severity in severity_dict:
                    print "\t\t%s: %s" % (severity[0], severity[1])

            # 20181105: 增加所有bug的严重程度分布。
            severity_dict = collections.Counter(map(lambda x: x["severity"], valid_bugs.values()))
            print "严重级别分布："
            for severity in severity_dict:
                print "\t%s: %s" % (severity, severity_dict[severity])

            # 20181105: 后端bug人员分布.
            background_bugs_dict = collections.Counter(
                filter(lambda x: x in users["后端"], map(lambda x: x["fixed_by"], valid_bugs.values())))
            # 20181218 增加后端人员严重级别分类
            print "后端bug分布："
            severity_map = ["1", "2", "3", "4"]
            severity_dict_all = []
            for fixed_by in background_bugs_dict:
                # print "\t%s: %s" % (fixed_by, background_bugs_dict[fixed_by]),
                severity_dict_per_fixed_by = collections.Counter(
                    map(lambda x: x["severity"], filter(lambda x: x["fixed_by"] == fixed_by, valid_bugs.values())))
                for severity in severity_map:
                    if severity not in severity_dict_per_fixed_by.keys():
                        severity_dict_per_fixed_by[severity] = 0
                severity_dict_per_fixed_by["total"] = reduce(lambda x, y: x + y, severity_dict_per_fixed_by.values())
                severity_dict_per_fixed_by["fixed_by"] = fixed_by
                severity_dict_all.append(severity_dict_per_fixed_by)
                for severity in severity_dict_per_fixed_by:
                    print "\t%s: %s" % (severity, severity_dict_per_fixed_by[severity]),
                print
            print "\t%s" % reduce(lambda x, y: x + "\t" + y, map(lambda x: x["fixed_by"], severity_dict_all))
            for severity in severity_map:
                print "%s\t%s" % (
                    severity, reduce(lambda x, y: x + "\t" + y, map(lambda x: str(x[severity]), severity_dict_all)))
            print "total\t%s" % reduce(lambda x, y: x + "\t" + y, map(lambda x: str(x["total"]), severity_dict_all))

        else:
            logging.warning("no bugs is available")

        for online_bug in online_bugs:
            if online_bug not in online_comments.keys():
                logging.error("%s: %s is not commented!" % (online_bug, online_bugs[online_bug]["title"]))
        print "amount of online bug: %s" % len(online_bugs)
        print "delay_release_count: %s" % delay_release_count
        print "normal_release_count: %s" % normal_release_count
        print "insert_release_count: %s" % insert_release_count
        print "released_stories: %s" % released_stories
        print "changed_stories_count: %s" % changed_stories_count
        print "p0_passed_count: %s" % p0_passed_count
        print "p0_failed_count: %s" % p0_failed_count
        if insert_stories:
            print "inserted stories:"
            for insert_story in insert_stories:
                print "\t" + insert_story

        print "#######################################end to analyze######################################"


if __name__ == '__main__':
    BugAnalysis = BugAnalysis(product_id=29, start_date="2019-01-01", end_date="2019-01-31")
    # BugAnalysis = BugAnalysis(product_id=29, month=12)
    BugAnalysis.main()

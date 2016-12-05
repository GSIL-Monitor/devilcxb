# -*- coding: utf-8 -*-
from jira.client import JIRA
import logging
logging.basicConfig(level=logging.INFO)


class HandleJira(object):
    def __init__(self, server, username, password):
        __options = None
        __oauth = None
        __validate = None
        __async = False
        __logging = False
        self.jira_client = JIRA(server, __options, (username, password), __oauth, __validate, __async, __logging)

    def report_condition(self, jql_str, reporter):
        """
        And reporter to filter condition
        :param jql_str: filter string
        :param reporter: reporter
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND reporter in (" + reporter + ")"
        else:
            return "reporter in (" + reporter + ")"

    def date_conditon(self, jql_str, start_date, end_date):
        """
        And start date and end date to filter condtion
        :param jql_str: filter string
        :param start_date: start date
        :param end_date: end date
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND created >= " + str(start_date)  + " AND created <= " + str(end_date)
        else:
            return jql_str + "created >= " + str(start_date)  + " AND created <= " + str(end_date)

    def update_date_conditon(self, jql_str, start_date, end_date):
        """
        And start date and end date to filter condtion
        :param jql_str: filter string
        :param start_date: start date
        :param end_date: end date
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND updated >= " + str(start_date)  + " AND updated <= " + str(end_date)
        else:
            return jql_str + "updated >= " + str(start_date)  + " AND updated <= " + str(end_date)

    def priority_condition(self, jql_str, priority_list):
        """
        And priority list to filter condtion
        :param jql_str: filter string
        :param priority_list: priority list
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND priority in (" + reduce(lambda x, y: x + ", " + y, priority_list) + ")"
        else:
            return jql_str + "priority in (" + reduce(lambda x, y: x + ", " + y, priority_list) + ")"

    def status_condition(self, jql_str, status_list):
        """
        And priority list to filter condtion
        :param jql_str: filter string
        :param status_list: status list
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND status in (" + reduce(lambda x, y: x + ", " + y, status_list) + ")"
        else:
            return jql_str + "status in (" + reduce(lambda x, y: x + ", " + y, status_list) + ")"

    def refused_reason_condition(self, jql_str, refused_reason_list):
        """
        And priority list to filter condtion
        :param jql_str: filter string
        :param status_list: status list
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND 拒绝原因 in (" + reduce(lambda x, y: x + ", " + y, refused_reason_list) + ")"
        else:
            return jql_str + "拒绝原因 in (" + reduce(lambda x, y: x + ", " + y, refused_reason_list) + ")"

    def filter_issue(self, reporter=None, start_date=None, end_date=None, priority_list=None, refused_start_date=None, refused_end_date=None, status_list=None, refused_reason_list=None):
        """
        filter issues via the filter condtion
        :param reporter: reporter
        :param start_date: start date
        :param end_date: end date
        :param priority_list: priority list
        :return: issues
        """
        jql_str = ""
        if reporter:
            jql_str = self.report_condition(jql_str, reporter)
        if start_date:
            jql_str = self.date_conditon(jql_str, start_date, end_date)
        if priority_list:
            jql_str = self.priority_condition(jql_str, priority_list)
        if refused_start_date:
            jql_str = self.update_date_conditon(jql_str, refused_start_date, refused_end_date)
        if status_list:
            jql_str = self.status_condition(jql_str, status_list)
        if refused_reason_list:
            jql_str = self.refused_reason_condition(jql_str, refused_reason_list)
        logging.info("filter conditions: " + jql_str)
        return self.jira_client.search_issues(jql_str=jql_str, maxResults=1000)


if __name__ == '__main__':
    HandleJira = HandleJira("http://jira.lab.tclclouds.com", "CITest", "tcltest123456")
    for issue in HandleJira.filter_issue("di.gao", "2016-07-01", "2016-07-31", ["严重", "致命", "一般"]):
        print issue.permalink()

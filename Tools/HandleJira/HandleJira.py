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

    def projects_condition(self, jql_str, projects):
        """
        And priority list to filter condtion
        :param jql_str: filter string
        :param projects: projects list
        :return: filter string
        """
        if jql_str:
            return jql_str + " AND project in (" + reduce(lambda x, y: x + ", " + y, projects) + ")"
        else:
            return jql_str + "project in (" + reduce(lambda x, y: x + ", " + y, projects) + ")"

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

    def filter_issue(self, reporter=None, start_date=None, end_date=None, priority_list=None, refused_start_date=None, refused_end_date=None, status_list=None, refused_reason_list=None, projects=None):
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
        if projects:
            jql_str = self.projects_condition(jql_str, projects)
        logging.info("filter conditions: " + jql_str)
        return self.jira_client.search_issues(jql_str=jql_str, maxResults=1000)

    def get_filed_value(self, issue_id, filed):
        """
        获取区域值
        :param issue_id: 问题的单号
        :param filed: 区域，请从[u'aggregateprogress', u'aggregatetimeestimate', u'aggregatetimeoriginalestimate', u'aggregatetimespent', u'assignee', u'attachment', u'comment', u'components', u'created', u'creator', u'customfield_10005', u'customfield_10008', u'customfield_10009', u'customfield_10010', u'customfield_10016', u'customfield_10017', u'customfield_10018', u'customfield_10023', u'customfield_10031', u'customfield_10032', u'customfield_10033', u'customfield_10034', u'customfield_10035', u'customfield_10100', u'customfield_10101', u'customfield_10202', u'customfield_10206', u'customfield_10221', u'customfield_10300', u'description', u'duedate', u'environment', u'fixVersions', u'issuelinks', u'issuetype', u'lastViewed', u'priority', u'progress', u'project', u'reporter', u'resolution', u'resolutiondate', u'status', u'subtasks', u'summary', u'timeestimate', u'timeoriginalestimate', u'timespent', u'timetracking', u'updated', u'versions', u'votes', u'watches', u'worklog', u'workratio']选择
        :return: 区域值
        """
        fileds = self.jira_client.issue(issue_id).fields
        return getattr(fileds,filed)

if __name__ == '__main__':
    HandleJira = HandleJira("http://jira.lab.tclclouds.com", "CITest", "tcltest123456")
    # print HandleJira.jira_client.issue("WEBCALL-5").fields.status
    # print HandleJira.filter_issue()
    # print HandleJira.get_filed_value("WEBCALL-5", "status")
    # print HandleJira.jira_client.issue_type("WEBCALL-5")
    # print HandleJira.jira_client.issue_link("WEBCALL-5")
    # print HandleJira.filter_issue("di.gao", "2016-07-01", "2016-07-31", ["严重", "致命", "一般"])
    monkey_issues = []
    issues = HandleJira.filter_issue(projects=["CI"], start_date="2016-11-21", end_date="2016-11-27")
    for issue in issues:
        Component = HandleJira.get_filed_value(issue, "components")[0].name
        monkey_issues.append(Component)
    import collections
    monkey_issues = collections.Counter(monkey_issues)
    for key in monkey_issues:
        print key, monkey_issues[key]

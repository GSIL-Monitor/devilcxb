#!/usr/bin/python
# -*- coding:utf-8 -*-

from jira.client import JIRA
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class MIEJIRA(object):
    """
    A bridge interface to connect CI and JIRA server
    
    This class provide basic actions to interact with JIRA server . 
    Includes three actions :
    1:Create issue
    2:Query issue
    3:Update issue
    4:Transition issue
    """

    # create a new MIEJIRA instance
    __t_jira = None

    # default jira server's address 
    __server = "http://jira.lab.tclclouds.com/"

    # default username and password 
    __basic_auth = ("CITest", "tcltest123456")

    # property extends from JIRA-Python library
    __options = None
    __oauth = None
    __validate = None
    __async = False
    __logging = False

    def __init__(self, server=None, basic_auth=None):
        """
        Construct a MIEJIRA client instance
        
        create a new JIRA instance to interact JIRA server
        
        Args:
            server: the server's address to interact
            basic_auth: a tuple pf username and password when establishing a session via HTTP BASIC authentication.
        """
        if server is not None:
            self.__server = server
        if basic_auth is not None:
            self.__basic_auth = basic_auth
        self.__t_jira = JIRA(self.__server, self.__options, self.__basic_auth, self.__oauth, self.__validate,
                             self.__async, self.__logging)

    def __get_component_id_by_name(self, component_name):
        components = self.__get_all_components("CI")
        if component_name in components.keys():
            component_id = components[component_name]
        else:
            raise Exception("Component name : %s is not exist , please check it" % component_name)
        return component_id

    def __get_all_components(self, projectname):
        formated_projects = {}
        project_ci = self.__t_jira.project(projectname)
        components = self.__t_jira.project_components(project_ci)
        for component in components:
            formated_projects[component.name] = component.id
        return formated_projects

    def create_issue(self, summary, description, component, reoccur_times, version, comment, priority="3"):

        """
        Create a new issue and return an issue Resource for it.

        :param summary: issue's summary information
        :param description: issue's detail information
        :param component: current issue's relative project . For example:AppCenter,GameCenter
        :param reoccur_times: issue re-occured times
        :param version: issue version
        :param comment: add comment
        :param priority: Id of priority. default value is 3
        :return: return a new dict that includes created issue_key,status_name,created_time,updated_time
        """
        print("********************Create New Issue****************************")
        # When create issue has succeed , return some scoped values to client
        return_value = {}

        # Maybe need to match it
        componentId = self.__get_component_id_by_name(component)
        print("component id : ", componentId)

        # Create issue dict property
        issue_dict = {
                "project": {
                    "key": "CI"
                },
                "summary": summary,
                "description": description,
                "versions": [{ "name": "None" }],
                "issuetype": {
                    "name": "CI Bug"
                },
                "priority": {
                    "id": priority
                },
                "customfield_10100": reoccur_times,
                "components": [
                    {
                        "id": componentId
                    }
                ],
                "customfield_10101": version
            }

        # First , let create a new issue
        created_issue = self.__t_jira.create_issue(fields=issue_dict)

        # Second , comment it
        # print("Begain comment")
        self.__t_jira.add_comment(created_issue.key, comment)
        # print("End comment")

        # combine the return values
        return_value["issue_key"] = created_issue.key
        return_value["status_name"] = created_issue.fields.status.name
        return_value["created_time"] = self.__format_time(created_issue.fields.created)
        return_value["updated_time"] = self.__format_time(created_issue.fields.updated)
        return_value["version_name"] = created_issue.fields.customfield_10101
        return return_value

    def query_issue_bykey(self, issue_keys):
        """
        Query issues's status and updated time
        
        Args:
            issue_keys: a tuple or list contains issue's keys to query
        
        Returns:
            return a new dict that contains each issue_keys's issue info 
            issue info include two fields: status_name , updated_time
        """
        print("************Query Issue*************")
        return_value = {}
        for issue_key in issue_keys:
            print("query issue_key : ", issue_key)
            issue = self.__t_jira.issue(issue_key)
            cur_info = (
            issue.fields.status.name, self.__format_time(issue.fields.updated), issue.fields.customfield_10101,
            issue.fields.customfield_10100)
            return_value[issue_key] = cur_info
        return return_value

    def query_issue(self, component, status):
        """
        According to status and component to query issues

        :param component: issue's component . Ex. APPCenter
        :param status: issue's status
        :return:
        return a dictionary of issue that fit the condition
        """
        print("**************Query Issue***************")
        return_value = []

        jql = "project = CI "

        if component:
            # Maybe need to match it
            componentId = self.__get_component_id_by_name(component)
            jql = jql + "AND component = " + componentId + " "

        if status:
            jql = jql + "AND status = " + status + " "

        issues = self.__t_jira.search_issues(jql, 0, 10000)

        for issue in issues:
            return_value.append(issue.key)

        return return_value

    def update_issue(self, issue_key, description, version, priority, reoccur_times, comment):
        """
        Update issue's fields

        :param issue_key: Key of the issue to perform the update action
        :param version: issue version
        :param priority: The id of priority action
        :param reoccur_times: occur times
        :param comment: issue's comment
        :return: if update action has succeed ,return True ; if not return False
        """
        print("***************************Update Issue******************")
        issue_dict = {}
        return_issue = None

        if description:
            issue_dict["description"] = description

        if version:
            issue_dict["customfield_10101"] = version

        if priority:
            issue_dict["priority"] = {
                "id": priority
            }
        if reoccur_times:
            issue_dict["customfield_10100"] = reoccur_times
        update_issue = self.__t_jira.issue(issue_key)
        update_issue.update(fields=issue_dict)
        # ADD COMMENT
        self.__t_jira.add_comment(update_issue.key, comment)

        queryed_issue = self.query_issue_bykey((issue_key,))
        return_issue = ((queryed_issue[issue_key])[0], (queryed_issue[issue_key])[1])
        return return_issue

    def transition_issue(self, issue_key, transition_name, comment_msg=None):
        """
        Transition issue's status, perform a transition on an issue.

        Args:
            issue_key: Key of the issue to perform the transition on
            transition_name: Name of the transition to perform
            comment: *Optional* String to add as comment to the issue when performing the transition.
        Returns:
            if update action has performed,return True. If not ,return False.
        """
        transition_id = None
        print("************Transition Issue*************")
        if transition_name == "CLOSE":
            # For real JIRA server CLOSE transition_id is 71
            # transition_id = "71"
            transition_id = ("71", "121")
            # transition_id = "2"
        elif transition_name == "REOPEN":
            # For real JIRA server REOPEN transition_id is 51
            # transition_id = "141"
            transition_id = ("141", "51")
            # transition_id = "3"
        else:
            raise Exception("transition name MUST BE CLOSE or REOPEN")
        update_flag = False
        issue = self.__t_jira.issue(issue_key)
        transitions = self.__t_jira.transitions(issue)
        for t in transitions:
            if t["id"] in transition_id:
                self.__t_jira.transition_issue(issue, t["id"], comment=comment_msg)
                update_flag = True
                break
        return update_flag

    def __format_time(self, time_str):
        """
        Format time
        
        "2015-04-28T13:19:53.000+0800" -> "2015-04-28 13:19:53"
        """
        formated_time = time_str[0:19].replace("T", " ")
        return formated_time

# if __name__ == '__main__':
#     jira = MIEJIRA()
#     for i in jira.query_issue('SHOP', 'Solved'):
#         print i

    # def query_issue_by_project(self):
    #         """
    #         According to status and component to query issues
    #
    #         :param component: issue's component . Ex. APPCenter
    #         :param status: issue's status
    #         :return:
    #         return a dictionary of issue that fit the condition
    #         """
    #         print("**************Query Issue***************")
    #         return_value = []
    #
    #         jql = "project = CI "
    #
    #         issues = self.__t_jira.search_issues(jql, 0, 10000)
    #
    #         for issue in issues:
    #             return_value.append(issue.key)
    #             # print issue
    #         return return_value
    #
    # def query_issue_by_key(self, issue_keys):
    #     """
    #     Query issues's status and updated time
    #
    #     Args:
    #         issue_keys: a tuple or list contains issue's keys to query
    #
    #     Returns:
    #         return a new dict that contains each issue_keys's issue info
    #         issue info include two fields: status_name , updated_time
    #     """
    #     print("************Query Issue*************")
    #     return_value = {}
    #     for issue_key in issue_keys:
    #         print("query issue_key : ", issue_key)
    #         issue = self.__t_jira.issue(issue_key)
    #         cur_info = (issue.fields.summary)
    #         # return_value[issue_key] = cur_info
    #         return_value[cur_info] = issue_key
    #     return return_value
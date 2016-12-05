# -*- coding: utf-8 -*-
from pymongo import MongoClient
import re


class HandleDatabase(object):
    def __init__(self):
        self.client = MongoClient('10.115.101.231', 27017)
        self.db = self.client['jira_issues']
        self.table = self.db["issues"]

    def query_db(self, project_name, details):
        query_result = {}
        for detail in details:
            if self.table.find({"project_name": project_name, "detail": detail}).count() == 0:
                details_db = self.table.find({"project_name": project_name})
                try:
                    filter_result = filter(lambda x: detail.replace(re.findall(".*(ProcessRecord\{.*?\))", detail)[0], "").strip() == x["detail"].strip().replace(re.findall(".*(ProcessRecord\{.*?\))", x["detail"])[0], ""), details_db)
                except IndexError:
                    filter_result = []
                if filter_result:
                    query_result[detail] = filter_result[0]
                else:
                    query_result[detail] = ()
            else:
                query_result[detail] = self.table.find({"project_name": project_name, "detail": detail})[0]
        return query_result

    def insert_db(self, insert_data):
        insert_data = map(
            lambda x: {"project_name": x[0], "apk_version": x[1], "type_id": x[2], "detail": x[3], "crash_count": x[4],
                       "devices": x[5], "jira_key": x[6], "current_time": x[7]}, insert_data)
        self.table.insert_many(insert_data)

    def get_all_info(self):
        table = self.db["pakckage_info"]
        log_dir = {}
        components_name = {}
        for i in table.find():
            components_name[i["package_name"]] = i["component_name"]
            log_dir[i["package_name"]] = str(i["log_dir"])
        return log_dir, components_name

    def close(self):
        self.client.close()


if __name__ == '__main__':
    db = HandleDatabase()
    details = ["Unable to start activity ComponentInfo{com.mig.contact/com.tcl.contacts.ui.activity.BackUpActivity}: java.lang.SecurityException: Permission Denial: opening provider com.android.providers.contacts.ContactsProvider2 from ProcessRecord{90130c5 22840:com.mig.contact/u0a197} (pid=22840, uid=10197) requires android.permission.READ_CONTACTS or android.permission.WRITE_CONTACTS//at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:2547)//"]
    print db.query_db("Contacts", details)
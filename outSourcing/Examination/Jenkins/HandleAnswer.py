# -*- coding: gb2312 -*-
import ConfigParser
import logging
import os
import datetime
import re
import sys
import chardet
logging.basicConfig(level=logging.INFO)


class HandleAnswer(object):
    def __init__(self):
        pass
        config = ConfigParser.ConfigParser()
        logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        self.totalQuestions = int(config.get("others", "total_questions"))
        sys.path.append(os.environ.get("WORKSPACE"))
        jenkins_server = config.get("config_jenkins", "server")
        jenkins_username = config.get("config_jenkins", "username")
        jenkins_password = config.get("config_jenkins", "password")
        from HandleJenkins.HandleJenkins import HandleJenkins
        self.HandleJenkins = HandleJenkins(jenkins_server, jenkins_username, jenkins_password)
        logging.info("get basic configuration of examination")
        self.job_xml = self.HandleJenkins.get_job_configurations(config.get("others", "basic_job"))
        from HandleMongoDB.HandleMongoDB import HandleMongoDB
        host = config.get("config_mongodb", "host")
        port = int(config.get("config_mongodb", "port"))
        outSourcing_db = config.get("config_mongodb", "database")
        questionBank_table = config.get("config_mongodb", "table")
        self.HandleMongoDB = HandleMongoDB(host, port)
        db_obj = self.HandleMongoDB.get_db(outSourcing_db)
        Examination_table = config.get("config_mongodb", "table_Examination")
        self.questionBank_table_ojb = self.HandleMongoDB.get_table(db_obj, questionBank_table)
        self.Examination_ojb = self.HandleMongoDB.get_table(db_obj, Examination_table)

    def get_questions(self):
        """
        获取题号和对应的题目
        Returns:题号和对应的题目

        """
        count = 1
        questions = {}
        while count < self.totalQuestions + 1:
            questions["题目" + str(count)] = self.HandleJenkins.get_descripotion_of_parameter(os.environ.get("JOB_NAME").decode("gb2312").encode("utf-8"), "题目".decode("gb2312").encode("utf-8") + str(count)).split("\n")[0]
            count += 1
        return questions

    def get_answers_actually(self):
        """
        获取题号和对应的答案
        Returns:题号和对应的答案

        """
        count = 1
        answers_actually = {}
        while count < self.totalQuestions + 1:
            answers_actually["题目" + str(count)] = os.environ.get("题目" + str(count))
            count += 1
        return answers_actually

    def get_answers_expected(self, questions):
        """
        获取实际的答案
        Args:
            questions: 题号和题目

        Returns:实际答案

        """
        answers_expected = {}
        for key in questions.keys():
            """
            print key
            try:
                print questions[key].decode(chardet.detect(questions[key])["encoding"]).encode("gb2312")
            except UnicodeEncodeError:
                try:
                    print type(questions[key])
                    print chardet.detect(questions[key])["encoding"]
                    print questions[key].decode(chardet.detect(questions[key])["encoding"])
                except:
                    print questions[key].encode(chardet.detect(questions[key])["encoding"]).decode("gb2312")
            """
            answers_expected[key] = self.HandleMongoDB.query_table(self.questionBank_table_ojb, {"question": questions[key]}, {"answer": 1})[0]["answer"]
        return answers_expected

    def get_mark(self, answers_expected, answers_actually):
        """
        计算分数
        Args:
            answers_expected: 期望答案
            answers_actually: 实际答案

        Returns: 分数

        """
        mark = 0
        for key in answers_expected.keys():
            if answers_actually[key]:
                if sorted(list(answers_expected[key])) == sorted(list(answers_actually[key].upper())):
                    mark += 2.5
        return mark

    def insert_to_db(self, details):
        """
        插入成绩信息
        Args:
            details: 成绩信息

        Returns:

        """
        self.HandleMongoDB.insert_item(self.Examination_ojb, details)
        logging.info("mark of " + details["Name"].decode("utf-8").encode("gb2312") + " is generated successfually")

    def get_start_time(self):
        """
        获取考试开始时间
        Returns:考试开始时间

        """
        return datetime.datetime.strptime(re.findall("(\d+-\d+-\d+ \d+:\d+:\d+)", os.environ.get("Note").decode("gb2312"))[0], "%Y-%m-%d %H:%M:%S")

    def main(self):
        questions = self.get_questions()
        # print questions
        answers_actually = self.get_answers_actually()
        # print answers_actually
        answers_expected = self.get_answers_expected(questions)
        mark = self.get_mark(answers_expected, answers_actually)
        details = {}
        details["Name"] = os.environ.get("Name").decode("gb2312").encode("utf-8")
        details["Mark"] = mark
        question_details = []
        for key in questions:
            question_each = {}
            question_each["No"] = key.decode("gb2312").encode("utf-8")
            question_each["Question"] = questions[key]
            question_each["Anser_Actually"] = answers_actually[key]
            question_each["Anser_Expected"] = answers_expected[key]
            question_details.append(question_each)
        details["Questions"] = question_details
        details["Generated_Time"] = str(datetime.datetime.now())
        start_time = self.get_start_time()
        end_time = datetime.datetime.now()
        details["Duration"] = (end_time - start_time).seconds/60
        self.insert_to_db(details)
        if os.path.isfile(os.path.join(os.environ.get("WORKSPACE"), "mail.txt")):
            os.remove(os.path.join(os.environ.get("WORKSPACE"), "mail.txt"))
        File = open(os.path.join(os.environ.get("WORKSPACE"), "mail.txt"), "w")
        File.write("mail_content=" + "mark is " + str(details["Mark"]) + "\n")
        File.write("mail_list=" + "xiaobo.chi@tcl.com, cc:zhanyu.huo@tcl.com" + "\n")
        File.write("mail_subject=Examination is finished for " + details["Name"])
        File.close()

if __name__ == '__main__':
    HandleAnswer = HandleAnswer()
    HandleAnswer.main()
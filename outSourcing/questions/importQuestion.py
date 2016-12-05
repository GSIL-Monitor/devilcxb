# -*- coding: utf-8 -*-
import xlrd
import ConfigParser
import logging
import os
logging.basicConfig(level=logging.INFO)


class importQuestion(object):
    def __init__(self, xls_File):
        """
        初始化导入题库，包括初始化数据库的连接
        Args:
            xls_File: 题库的excel文件的绝对路径

        Returns:

        """
        config = ConfigParser.ConfigParser()
        logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        from Tools.HandleMongoDB.HandleMongoDB import HandleMongoDB
        host = config.get("config_mongodb", "host")
        port = int(config.get("config_mongodb", "port"))
        outSourcing_db = config.get("config_mongodb", "database")
        questionBank_table = config.get("config_mongodb", "table")
        self.HandleMongoDB = HandleMongoDB(host, port)
        db_obj = self.HandleMongoDB.get_db(outSourcing_db)
        self.questionBank_table_ojb = self.HandleMongoDB.get_table(db_obj, questionBank_table)
        self.xls_obj = xlrd.open_workbook(xls_File)

    def insert_question(self, question):
        """
        更新题库
        Args:
            question: 更新的题内容

        Returns: None

        """
        question["component_id"] = int(question["component_id"])
        question["question_id"] = int(question["question_id"])
        if not self.HandleMongoDB.query_table(self.questionBank_table_ojb, question):
            self.HandleMongoDB.insert_item(self.questionBank_table_ojb, question)
        else:
            self.HandleMongoDB.update_item(self.questionBank_table_ojb, {"component_id": question["component_id"], "question_id": question["question_id"], "question": question["question"]}, question)

    def close_mongo(self):
        """
        关闭Mongodb连接
        Returns: None

        """
        self.HandleMongoDB.close_mongodb()

    def get_questions(self, sheet_obj):
        """
        从excel里面获取题
        Args:
            sheet_obj: sheet object

        Returns: 所有的题

        """
        questions = []
        for i in range(sheet_obj.nrows):
            questions.append(sheet_obj.row_values(i))
        if questions[0][0] == "component_id":
            questions = map(lambda x: dict(zip(questions[0],x)), questions[1:])
        return questions

    def main(self):
        for sheet_obj in self.xls_obj.sheets():
            #sheet_obj = importQuestion.get_sheet_ojb(sheet_name)
            questions = self.get_questions(sheet_obj)
            for question in questions:
                # print question
                self.insert_question(question)
        self.close_mongo()


if __name__ ==  "__main__":
    importQuestion = importQuestion("questions.xlsx")
    importQuestion.main()



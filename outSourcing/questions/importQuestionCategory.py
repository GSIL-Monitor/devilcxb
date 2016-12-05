# -*- coding: utf-8 -*-
import xlrd
import ConfigParser
import logging
import os
logging.basicConfig(level=logging.INFO)


class importQuestionCategory(object):
    def __init__(self, xls_File):
        """
        初始化导入题库类别，包括初始化数据库的连接
        Args:
            xls_File: 题库类别的excel文件的绝对路径

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
        questionBankCategory_table = config.get("config_mongodb", "table_questionCategory")
        self.HandleMongoDB = HandleMongoDB(host, port)
        db_obj = self.HandleMongoDB.get_db(outSourcing_db)
        self.questionBank_table_ojb = self.HandleMongoDB.get_table(db_obj, questionBank_table)
        self.questionBankCategory_table_ojb = self.HandleMongoDB.get_table(db_obj, questionBankCategory_table)
        self.xls_obj = xlrd.open_workbook(xls_File)

    def insert_questionCategory(self, question):
        """
        更新题库
        Args:
            question: 更新题库类别内容

        Returns: None

        """
        question["component_id"] = int(question["component_id"])
        question["questionsNumber"] = len(self.HandleMongoDB.query_table(self.questionBank_table_ojb, {"component_id": question["component_id"]}))
        if not self.HandleMongoDB.query_table(self.questionBankCategory_table_ojb, question):
            self.HandleMongoDB.insert_item(self.questionBankCategory_table_ojb, question)
        else:
            self.HandleMongoDB.update_item(self.questionBankCategory_table_ojb, {"component_id": question["component_id"], "category": question["category"]}, question)

    def close_mongo(self):
        """
        关闭Mongodb连接
        Returns: None

        """
        self.HandleMongoDB.close_mongodb()

    def get_questionsCategory(self, sheet_obj):
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
        questionsCategory = self.get_questionsCategory(self.xls_obj.sheets()[0])
        for question in questionsCategory:
            # print question
            self.insert_questionCategory(question)
        self.close_mongo()


if __name__ ==  "__main__":
    importQuestionCategory = importQuestionCategory("question_category.xlsx")
    importQuestionCategory.main()



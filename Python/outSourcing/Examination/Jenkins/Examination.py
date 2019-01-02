# -*- coding: utf-8 -*-
import ConfigParser
import os
import random
import datetime
import sys
import logging
logging.basicConfig(level=logging.INFO)


class Examination(object):
    def __init__(self):
        """
        init Examination
        Returns: None

        """
        logging.info("#####################start############################")
        self.candidate = os.environ.get("candidate").decode("gb2312").encode("utf-8")
        config = ConfigParser.ConfigParser()
        logging.info(os.path.join(os.path.dirname(__file__), "conf.ini"))
        config.readfp(open(os.path.join(os.path.dirname(__file__), "conf.ini")))
        self.totalQuestions = int(config.get("others", "total_questions"))
        self.exceptQuestionCategory = config.get("others", "except_category").split(",")
        jenkins_server = config.get("config_jenkins", "server")
        jenkins_username = config.get("config_jenkins", "username")
        jenkins_password = config.get("config_jenkins", "password")
        logging.info("###################initial Jenkins connection and get configuration of job Examination#######################")
        sys.path.append(os.environ.get("WORKSPACE"))
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
        questionCategory_table = config.get("config_mongodb", "table_questionCategory")
        self.questionBank_table_ojb = self.HandleMongoDB.get_table(db_obj, questionBank_table)
        self.questionCategory_ojb = self.HandleMongoDB.get_table(db_obj, questionCategory_table)
        logging.info("######################start to handle xml#####################")
        from HandleXML.HandleXML import HandleXML
        self.HandleXML = HandleXML(self.job_xml)

    def get_totalQuestionFromMOngodb(self):
        """
        从数据库里面获取所有当前有效的考题
        Returns: 所有考核项的id和题量，所有当前有效的考题

        """
        questionCategory_idsAndquestionsNumber = self.HandleMongoDB.query_table(self.questionCategory_ojb, {"category": {"$nin": self.exceptQuestionCategory}}, {"component_id": 1, "questionsNumber": 1})
        totalQuestionsFromMongodb = self.HandleMongoDB.query_table(self.questionBank_table_ojb, {"component_id": {"$in": map(lambda x: x["component_id"], questionCategory_idsAndquestionsNumber)}})
        return questionCategory_idsAndquestionsNumber, totalQuestionsFromMongodb

    def get_rate(self, totalQuestionsFromMongodb):
        """
        根据总体量和需要考核的题量，得到比例
        Args:
            totalQuestionsFromMongodb: 所有当前有效的考题

        Returns: 比例

        """
        return float(len(totalQuestionsFromMongodb))/float(self.totalQuestions)

    def get_questionNumberMapping(self, questionCategory_idsAndquestionsNumber, rate):
        """
        根据比例算出每个部分需要提供的题量
        Args:
            questionCategory_idsAndquestionsNumber: 所有考核项的id和题量
            rate: 比例

        Returns: 每个考核项的题量

        """
        questionNumberMapping = {}
        for item in questionCategory_idsAndquestionsNumber:
            questionNumberMapping[item["component_id"]] = int(round(item["questionsNumber"]/rate))

        error = reduce(lambda x, y: x + y, questionNumberMapping.values()) - self.totalQuestions
        logging.info("error number is: " + str(error))
        randomKey = random.choice(questionNumberMapping.keys())
        logging.info("total questions from filter: " + str(reduce(lambda x, y: x+ y, questionNumberMapping.values())))
        questionNumberMapping[randomKey] = questionNumberMapping[randomKey] - error
        return questionNumberMapping

    def get_questions(self, questionNumberMapping, totalQuestionsFromMongodb):
        """
        返回所有的题
        Args:
            questionNumberMapping: 每个考核项的题量和ID
            totalQuestionsFromMongodb: 所有当前有效的考题

        Returns: 返回本次考核的考题

        """
        return reduce(lambda x, y: x + y, map(lambda id: random.sample(filter(lambda x: x["component_id"] == id, totalQuestionsFromMongodb), questionNumberMapping[id]), questionNumberMapping.keys()))

    def create_StringElement(self, name, description):
        """
        增加题目
        Args:
            name:  题号
            description: 题目

        Returns: 创建的题目element

        """
        StringParameterDefinition = self.HandleXML.createElement("hudson.model.StringParameterDefinition")
        name_element = self.HandleXML.createElement("name")
        self.HandleXML.appendChildElement(name_element, self.HandleXML.createTextNode(name))
        description_element = self.HandleXML.createElement("description")
        self.HandleXML.appendChildElement(description_element, self.HandleXML.createTextNode(description))
        defaultValue_element = self.HandleXML.createElement("defaultValue")
        self.HandleXML.appendChildElement(StringParameterDefinition, name_element)
        self.HandleXML.appendChildElement(StringParameterDefinition, description_element)
        self.HandleXML.appendChildElement(StringParameterDefinition, defaultValue_element)
        return StringParameterDefinition

    def main(self):
        logging.info("####################generate questions from questionBank######################")
        questionCategory_idsAndquestionsNumber, totalQuestionsFromMongodb = self.get_totalQuestionFromMOngodb()
        logging.info("questionCategory_idsAndquestionsNumber: " + str(questionCategory_idsAndquestionsNumber))
        logging.info("length of totalQuestionsFromMongodb: " + str(len(totalQuestionsFromMongodb)))
        rate = self.get_rate(totalQuestionsFromMongodb)
        logging.info("rate: " + str(rate))
        questionNumberMapping = self.get_questionNumberMapping(questionCategory_idsAndquestionsNumber, rate)
        logging.info("questionNumberMapping: " + str(questionNumberMapping))
        questions = self.get_questions(questionNumberMapping, totalQuestionsFromMongodb)
        logging.info("number of questions: " + str(len(questions)))
        logging.info("######################start to handle xml#####################")
        parameterDefinitions_element = self.HandleXML.getElementViaNodeName("parameterDefinitions")
        element_string = self.HandleXML.getElementViaNodeName("hudson.model.StringParameterDefinition")
        defaultValue_element_stringParameter = self.HandleXML.getElementViaNodeName("defaultValue", element_string)
        if self.HandleXML.getNodeName(defaultValue_element_stringParameter) == "defaultValue" and self.HandleXML.getNodeValue(defaultValue_element_stringParameter) == u"待考试人姓名":
            self.HandleXML.setNodeValue(defaultValue_element_stringParameter, self.candidate)
        # print self.HandleXML.doc.toxml(encoding='utf-8')
        element_text = self.HandleXML.getElementViaNodeName("hudson.model.TextParameterDefinition")
        defaultValue_element_textParameter = self.HandleXML.getElementViaNodeName("defaultValue", element_text)
        if self.HandleXML.getNodeName(defaultValue_element_textParameter) == "defaultValue" and u"考试开始时间：" in self.HandleXML.getNodeValue(defaultValue_element_textParameter):
            self.HandleXML.setNodeValue(defaultValue_element_textParameter, self.HandleXML.getNodeValue(defaultValue_element_textParameter).encode("utf-8").replace("考试开始时间：", "考试开始时间：" + str(datetime.datetime.now())))
        # print self.HandleXML.doc.toxml(encoding='utf-8')
        count = 1
        for question_item in questions:
            name = u"题目".encode("utf-8") + str(count)
            if not type(question_item["question"]) == float:
                question = question_item["question"].encode("utf-8")
            else:
                question = str(int(question_item["question"]))
            if not type(question_item["selection_A"]) == float:
                selection_A = question_item["selection_A"].encode("utf-8")
            else:
                selection_A = str(int(question_item["selection_A"]))
            if not type(question_item["selection_B"]) == float:
                selection_B = question_item["selection_B"].encode("utf-8")
            else:
                selection_B = str(int(question_item["selection_B"]))
            if not type(question_item["selection_C"]) == float:
                selection_C = question_item["selection_C"].encode("utf-8")
            else:
                selection_C = str(int(question_item["selection_C"]))
            if not type(question_item["selection_D"]) == float:
                selection_D = question_item["selection_D"].encode("utf-8")
            else:
                selection_D = str(int(question_item["selection_D"]))
            description = question + "\n" + "A." + selection_A + "\n" + "B." + selection_B + "\n" + "C." + selection_C + "\n" + "D." + selection_D
            # description = description.replace("\\", "\\\\")
            self.HandleXML.appendChildElement(parameterDefinitions_element, self.create_StringElement(name, description))
            count += 1
        f = open("test1.xml", "w")
        self.HandleXML.doc.writexml(f, encoding='utf-8')
        f.close()
        from HandleXML.HandleXML import HandleXML
        HandleXML_again = HandleXML("test1.xml")
        self.HandleJenkins.create_job("Examination_" + self.candidate, HandleXML_again.doc.toxml(encoding="utf-8"))
        logging.info("please enter to the url and start examination: " + self.HandleJenkins.jenkins_server + "job/" + "Examination_" + self.candidate.decode("utf-8").encode("gb2312") + "/build?delay=0sec")
        #self.HandleXML.doc.toxml(encoding='utf-8') bug 需要处理一下

if __name__ == '__main__':
    Examination = Examination()
    Examination.main()
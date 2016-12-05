# -*- coding: utf-8 -*-
from xml.dom.minidom import parse, parseString
import os
import logging
logging.basicConfig(level=logging.INFO)
import datetime


class HandleXML(object):
    def __init__(self, pathOrSource):
        """
        初始化处理xml文件
        :param pathOrSource: xml文件的路径或者xml的文本流
        :return: None
        """
        if os.path.isfile(pathOrSource):
            self.doc = parse(pathOrSource)
        elif type(pathOrSource) == unicode:
            self.doc = parseString(pathOrSource.encode("utf-8"))
        elif type(pathOrSource) == str:
            self.doc = parseString(pathOrSource)
        logging.info("xml tree is generated!")

    def getElementViaNodeName(self, tagName, basedElement=None, index=0):
        """
        返回element
        :param tagName: 节点名称
        :param basedElement: 基于的element对象
        :param index: 第几个
        :return: 返回element
        """
        if basedElement:
            logging.info("basedElement is:" + str(basedElement))
            return basedElement.getElementsByTagName(tagName)[index]
        return self.doc.getElementsByTagName(tagName)[index]

    def createElement(self, tagName):
        """
        创建Element, 返回创建的element对象
        :param tagName: 节点名称
        :return: 返回创建的element对象
        """
        logging.info("element will be created and the tag name is " + tagName)
        return self.doc.createElement(tagName)

    def createTextNode(self, text):
        """
        给创建的Element设置文本
        :param createdElement: 创建的Element
        :return: None
        """
        return self.doc.createTextNode(text)

    def appendChildElement(self, basedElement, createdElement):
        """
        追加element到父element
        :param basedElement: 父element
        :param createdElement: 创建的子element
        :return: None
        """
        basedElement.appendChild(createdElement)
        logging.info(str(createdElement) + " is appended for " + str(basedElement))

    def setNodeValue(self, element_obj, text):
        """
        设置tag的内容
        :param element_obj: element对象
        :param text:tag的内容
        :return:
        """
        element_obj.firstChild.replaceWholeText(text)
        logging.info(text + " is set to " + str(element_obj))

    def getNodeName(self, element_obj):
        """
        返回节点名称
        :param element_obj: element对象
        :return:节点名称
        """
        return element_obj.nodeName

    def getNodeValue(self, element_obj):
        """
        返回节点内容
        :param element_obj: element对象
        :return:节点内容
        """
        return element_obj.childNodes[0].nodeValue


if __name__ == "__main__":
    """
    from Tools.HandleJenkins.HandleJenkins import HandleJenkins
    HandleJenkins = HandleJenkins("http://10.115.101.230:8080/jenkins/", "jenkins.cdval", "I8IBz0U2TC")
    source = HandleJenkins.get_job_configurations("Examination")
    HandleXML = HandleXML(source)
    #print HandleXML.doc.toxml("utf-8")
    parameterDefinitions_element = HandleXML.getElementViaNodeName("parameterDefinitions")

    StringParameterDefinition_element = HandleXML.createElement("hudson.model.StringParameterDefinition")
    name_element = HandleXML.createElement("name")
    description_element = HandleXML.createElement("description")
    description_element.appendChild(HandleXML.createTextNode("description"))
    defaultValue_element = HandleXML.createElement("defaultValue")
    HandleXML.appendChildElement(StringParameterDefinition_element, description_element)
    HandleXML.appendChildElement(StringParameterDefinition_element, defaultValue_element)
    HandleXML.appendChildElement(parameterDefinitions_element, StringParameterDefinition_element)

    for element in HandleXML.doc.getElementsByTagName("hudson.model.StringParameterDefinition"):
        for name_element in element.getElementsByTagName("defaultValue"):
            if name_element.nodeName == "defaultValue" and name_element.childNodes[0].nodeValue == u"待考试人姓名":
                HandleXML.setNodeValue(name_element, u"苟娟")
                break
        break
    for element in HandleXML.doc.getElementsByTagName("hudson.model.TextParameterDefinition"):
        for name_element in element.getElementsByTagName("defaultValue"):
            if name_element.nodeName == "defaultValue" and u"考试开始时间：" in name_element.childNodes[0].nodeValue:
                HandleXML.setNodeValue(name_element, name_element.childNodes[0].nodeValue.replace(u"考试开始时间：", u"考试开始时间：" + str(datetime.datetime.now().time().strftime("%H:%M:%S"))))
                break
        break
                # print childNode.toxml("utf-8")
    print HandleXML.doc.toxml("utf-8")
    #print HandleXML.doc.getElementsByTagName("hudson.model.StringParameterDefinition")[1].getElementsByTagName("description")[0].nodeValue
    """
    HandleXML = HandleXML("test1.xml")
    print HandleXML.doc.toxml()
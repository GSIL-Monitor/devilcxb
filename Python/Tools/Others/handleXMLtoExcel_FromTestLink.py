# -*- coding: cp936 -*-
# Author: Chi Xiaobo
# Purpose: To handle the XML test case and formated to Excel
# Try to install xlwt.
# !Note, Only xls can be saved.
# Please specify your XML file firstly.
# Aug 31 2015, first release

from xml.dom.minidom import parse, parseString
import xlwt
import re

class handleXMLtoExcel(object):

    def __init__(self, xml):
        self.xml = xml
        self.doc = parse(xml)    

    def my_cmp(self,v1, v2):
        p = re.compile("(\d+)")
        d1 = [int(i) for i in p.findall(v1)][0]
        d2 = [int(i) for i in p.findall(v2)][0]
        return cmp(d1, d2)

    def replace_html(self,s):
        s = s.replace('&quot;','"')
        s = s.replace('&amp;','&')
        s = s.replace('&lt;','<')
        s = s.replace('&gt;','>')
        s = s.replace('&nbsp;',' ')
        s = s.replace('&ldquo;',' ')
        s = s.replace('&rdquo;',' ')
        s = s.replace('<br />','\n')
        return s

    def set_style(self,name,height,bold=False):
        style = xlwt.XFStyle() # 初始化样式
        font = xlwt.Font() # 为样式创建字体
        font.name = name # 'Times New Roman'
        font.bold = bold
        font.color_index = 4
        font.height = height 
        style.font = font
        return style

    def write_excel(self,caseDetails,Keys,sheet,rowNumber):
        for i in range(0, len(Keys)):
            sheet.write(rowNumber + i,0,self.replace_html(Keys[i]),self.set_style('Times New Roman',220,True))
            sheet.write(rowNumber + i,1,self.replace_html(caseDetails[Keys[i]]),self.set_style('Times New Roman',220,True))        
        rowNumber = rowNumber + len(caseDetails.keys()) + 1
        return rowNumber

    def getTestCases(self,doc):
        set_TestCases = []
        testSuites = doc.getElementsByTagName('testsuite')
        for testSuite in testSuites:
            if testSuite.parentNode == testSuites[0]:
                temp_set_TestCases = []
                temp_set_TestCases.append(testSuite.getAttribute("name"))
                testCases = testSuite.getElementsByTagName('testcase')
                for testCase in testCases:
                    temp_set_TestCases.append(testCase.getAttribute("internalid"))
                set_TestCases.append(temp_set_TestCases)        
        return set_TestCases     

    def getCaseDetails(self,doc, caseID):
        caseDetails = {}
        Keys = ["caseName"]
        caseObjects = ["summary", "preconditions", "actions", "expectedresults"]
        testCases = doc.getElementsByTagName('testcase')
        for testCase in testCases:
            if testCase.getAttribute("internalid") == caseID:
                caseDetails["caseName"] = testCase.getAttribute("name")
                for caseObject in caseObjects:
                    items,Key = self.getNodeValue(testCase, caseObject)
                    caseDetails = self.updateDict(caseDetails,items)
                    Keys = Keys + Key
        return caseDetails, Keys
            
            
    def updateDict(self,old,new):
        old.update(new)
        return old

    def getNodeValue(self,testCase,NodeName):
        items = {}
        Keys = []
        Nodes = testCase.getElementsByTagName(NodeName)
        if len(Nodes) != 0:
            count = 1
            for Node in Nodes:
                if len(Node.childNodes) == 0:
                    Keys.append(NodeName)
                    items[NodeName] = "NA"
                else:
                    for childNode in Node.childNodes:
                        if NodeName == "actions" or NodeName == "expectedresults":
                            Keys.append(NodeName + str(count))
                            items[NodeName + str(count)] = childNode.nodeValue.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>", "").strip()
                        else:
                            Keys.append(NodeName)
                            items[NodeName] = childNode.nodeValue.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>", "").strip()
                count += 1
        else:
            Keys.append(NodeName)
            items[NodeName] = "NA"
        return items,Keys

if __name__ == '__main__':

    xml = "Carrier App Setup.testproject-deep.xml"
    f = xlwt.Workbook(style_compression=2) #创建工作簿
    handleXMLtoExcel = handleXMLtoExcel(xml)
    testCases = handleXMLtoExcel.getTestCases(handleXMLtoExcel.doc)
    for testCases_eachTestSet in testCases:
        rowNumber = 0
        caseDetails_eachTestSet = []
        Keys_eachTestSet = []
        for caseID in testCases_eachTestSet[1:]:
            caseDetails, Keys = handleXMLtoExcel.getCaseDetails(handleXMLtoExcel.doc, caseID)
            caseDetails_eachTestSet.append(caseDetails)
            Keys_eachTestSet.append(Keys)
        sheet = f.add_sheet(testCases_eachTestSet[0],cell_overwrite_ok=True)
        for caseDetails in caseDetails_eachTestSet:
            rowNumber = handleXMLtoExcel.write_excel(caseDetails,Keys_eachTestSet[caseDetails_eachTestSet.index(caseDetails)],sheet,rowNumber)
    f.save(xml.replace(".xml", "") + ".xls")

from xml.dom.minidom import parse


class compareTestResultt(object):
    def __init__(self, withoutAPK_result_xml, withAPK_result_xml):
        self.withoutAPK_result_xml = withoutAPK_result_xml
        self.withAPK_result_xml = withAPK_result_xml

    def nice_print(self, message, sign='*'):
        '''
            Printing nice banners
        '''
        print(''.join([' ', sign*len(message)]))
        print(''.join([' ', message]))
        print(''.join([' ', sign*len(message)]))

    def get_test_suits(self, element,parent_list):
        parent_list.append(element.getAttribute("name"))
        if element.nodeName == "TestSuite":
            self.get_test_suits(element.parentNode,parent_list)
        elif element.nodeName == "TestPackage":
            pass
        return parent_list

    def get_details(self, xml_file):
        doc = parse(xml_file)
        #print doc.getElementsByTagName("TestPackage")
        caseDetails = {}
        for FailedScene_element in  doc.getElementsByTagName("FailedScene"):
            testName = FailedScene_element.parentNode
            testCase = testName.parentNode
            parent_list = self.get_test_suits(testCase.parentNode, parent_list = [])
            parent_list.reverse()
            parent_list.append(testCase.getAttribute("name"))
            parent_list.append(testName.getAttribute("name"))
            caseDetails[reduce(lambda x,y:x + "." + y, parent_list)] = FailedScene_element.getAttribute("message")
        print caseDetails.keys()
        return  caseDetails

    def compare_result(self, withoutAPK_details, withAPK_details):
        if len(filter(lambda x: x not in withoutAPK_details.keys(), withAPK_details.keys())) == 0 and len(filter(lambda x: withAPK_details[x] != withoutAPK_details[x], withAPK_details.keys())) == 0:
            self.nice_print("CTS test is Passed!")
        else:
            for key in filter(lambda x: x not in withoutAPK_details.keys(), withAPK_details.keys()):
                self.nice_print(key)
                print withAPK_details[key]
            for key in filter(lambda x: withAPK_details[x] != withoutAPK_details[x], filter(lambda x: x in withoutAPK_details.keys(), withAPK_details.keys())):
                self.nice_print(key)
                print withoutAPK_details[key]
                print withAPK_details[key]
    def main(self):
        withoutAPK_details = self.get_details(self.withoutAPK_result_xml)
        withAPK_details = self.get_details(self.withAPK_result_xml)
        self.compare_result(withoutAPK_details, withAPK_details)

if "__main__" == __name__:
    compare_test_result = compareTestResultt("testResult_without.xml","testResult_with.xml")
    compare_test_result.main()

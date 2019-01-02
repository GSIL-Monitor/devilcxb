from xml.dom.minidom import parse, parseString
import datetime
import os
from BeautifulSoup import BeautifulSoup, Tag

def get_summary():
    summary = []
    job_path = os.environ.get("WORKSPACE")
    case_root_path = os.path.join(job_path, r"projects\YelloPages\SocketAutoTest")
    argumentFile_path = os.path.join(case_root_path, r"config\runArgument.txt")
    contents = open(argumentFile_path).readlines()
    suites = map(lambda x: x.strip(), list(set(filter(lambda x: contents[contents.index(x) -1].strip() == "--suite", contents))))
    # print suites
    doc = parse("output.xml")
    testSuites = doc.getElementsByTagName('stat')
    for testSuite in testSuites:
        for node in testSuite.childNodes:
            if node.nodeValue in suites:
                passed_cases = int(testSuite.getAttribute("pass"))
                failed_cases = int(testSuite.getAttribute("fail"))
                summary.append([node.nodeValue.split(".")[-1], passed_cases, failed_cases, passed_cases + failed_cases])
    return summary

def generate_table(summary):
    soup = BeautifulSoup()
    new_tag_table = Tag(soup, "table")
    new_tag_table["border"] = 1
    new_tag_table["cellspacing"] = 0
    new_tag_table["cellpadding"] = 0
    new_tag_table["bordercolordark"] = "#000000"
    new_tag_table["cellspacing"] = "#ffffff"
    soup.append(new_tag_table)
    new_Tag_tr = Tag(soup, "tr")
    new_Tag_tr["bgcolor"] = "#0072E3"
    new_tag_table.append(new_Tag_tr)
    for i in ["TestSuite", "Passed", "Failed", "Total"]:
        new_Tag_td = Tag(soup, "td")
        new_Tag_td.string = str(i)
        new_Tag_tr.append(new_Tag_td)
    for i in summary:
        new_Tag_tr = Tag(soup, "tr")
        new_tag_table.append(new_Tag_tr)
        for j in i:
            new_Tag_td = Tag(soup, "td")
            new_Tag_td.string = str(j)
            new_Tag_tr.append(new_Tag_td)
    print str(soup.prettify())
    return str(soup.prettify())


date = str(datetime.datetime.now()).split()[0]
#job_name = "TCL-Market_Testing_Mutilple_Versions_Windows"
job_name = os.environ.get("JOB_NAME")
#job_path = r"C:\Jenkins\workspace\TCL-Market_Testing_Mutilple_Versions_Windows"
job_path = os.environ.get("WORKSPACE")
#BUILD_URL = "http://10.115.101.230:8080/jenkins/view/TCL_Market/job/TCL-Market_Testing_Mutilple_Versions_Windows/64/"
BUILD_URL = os.environ.get("BUILD_URL")
mail_content = ""
report = BUILD_URL + "artifact/" + "report.html"
print report
log_url = BUILD_URL + "console"
summary = get_summary()
table = generate_table(summary)
mail_content = table
# mail_content = "Report URL" + ":<br />  " + '<a href=' + report + ' target="_blank">' + report + '</a><br /><br />' + "Log URL" + ":<br />  " + '<a href=' + log_url + ' target="_blank">' + log_url + '</a><br /><br />Summary: <br />' + table + '<br /><br />BR<br />VAL Team'
if os.path.isfile(os.path.join(job_path, "report.html")):
    mail_list = "xiaobo.chi@tcl.com"
    #mail_list = "cc:xiaobo.chi@tcl.com,cc:wei.y@tcl.com,cc:zhanyu.huo@tcl.com,tingtinghe@tcl.com, di.gao@tcl.com,cc:leisun@tcl.com,zhoupei.he@tcl.com"
else:
    mail_list = "xiaobo.chi@tcl.com"
    mail_content = "report is generated failed!"
#mail_list = "xiaobo.chi@tcl.com"
File = open("mail.txt", "w")
File.write("mail_list=" + mail_list + "\n")
File.write("mail_content=" + mail_content + "\n")
File.write("date=" + date + "\n")
File.write("mail_subject=" + job_name + "_")
File.close()

# -*- coding: cp936 -*-
import urllib
import urllib2
import cookielib
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import datetime
import time
import sys

def get_week_number():
    return str(time.strftime("%Y")) + " Week " + str(int(time.strftime("%W")))

def create_page(url, title):
    params = {"os_username":"xiaobo.chi", "os_password":"DEVIL_cxb123", "title": title}
    # decode into url format
    params = urllib.urlencode(params)
    #print params
    u1 = urllib2.urlopen(url)
    click_button_id = re.findall('id="(.*?)"',filter(lambda x: 'name="confirm"' in x, u1.read().split("\n"))[0])[0]
    #print click_button_id
    #driver = webdriver.Firefox(timeout=30)
    time.sleep(4)
    driver.get(url + "&" + params)
    time.sleep(4)
    driver.find_element_by_id(click_button_id).click()
    time.sleep(4)
    #driver.quit()
    
def get_create_page(url):
    return re.findall('href="(.*?")',filter(lambda x: "createPageLink" in x, urllib2.urlopen(url).read().split("\n"))[0])[0].replace('"', "").replace('&amp;', "&")

def get_code(url):
    try:
        if urllib2.urlopen(url).getcode() == 200:
            return True
        else:
            return False
    except urllib2.HTTPError:
        return False
    
def get_contents(url):
    return urllib2.urlopen(url).read().split("\n")

def remove_bullet(title_week):
    driver.switch_to.frame("wysiwygTextarea_ifr")
    flag = False
    tag_lies = driver.find_elements_by_tag_name("li")
    for tag_li in tag_lies:
        try:
            #print tag_li.find_element_by_tag_name("a").text
            if title_week in tag_li.find_element_by_tag_name("a").text and tag_li.find_element_by_tag_name("a").text != title_week:
                #print tag_li.find_element_by_tag_name("a").text
                flag = True
                #break
        except exceptions.NoSuchElementException:
            pass
    return flag

domain = "http://confluence.lab.tclclouds.com"
weekly_report_base = "http://confluence.lab.tclclouds.com/display/MIECD"
weekly_report_home = 'http://confluence.lab.tclclouds.com/display/MIECD/00+-+Weekly+Status+Report'
week_create_home = "http://confluence.lab.tclclouds.com/pages/createpage.action?spaceKey=MIECD&fromPageId=1508281"
params = {"os_username":"xiaobo.chi", "os_password":"DEVIL_cxb123"}
# decode into url format
params = urllib.urlencode(params)

# Save login information
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
urllib2.install_opener(opener)
# open a website with params to save the autherization info.
weekly_report_home_request = urllib2.urlopen(weekly_report_home, params)

#create week page.
title_week = get_week_number()
week_url = weekly_report_base + "/" + title_week.replace(" ", "+")

global driver
driver = webdriver.Firefox(timeout=30)
if get_code(week_url) == False:
    create_page(week_create_home, title_week)
else:
    print "no need to create the url as below!"
    print week_url
content_week = get_contents(week_url)
# create department page.
department_create_page = domain + get_create_page(week_url)
department_titles = ["HR(CD)", "Feng's Report", "Java Report", "Front End Report", "PD Report", "Android Report", "VAL Report"]
department_titles = map(lambda x: title_week + " - " + x, department_titles)
for department_title in department_titles:
    if get_code(weekly_report_base + "/" + department_title.replace(" ", "+")) == False:
        create_page(department_create_page, department_title)
    else:
        print "no need to create the url as below!"
        print weekly_report_base + "/" + department_title.replace(" ", "+")

week_edit_url = domain + re.findall('href="(.*?")', filter(lambda x: "editPageLink" in x, content_week)[0])[0].replace('"', "")
#print week_edit_url
content_week_edit = get_contents(week_edit_url)
#print content_week_edit
bullet_button_id = re.findall('id="(.*?")', filter(lambda x: "Bullet list" in x, content_week_edit)[0])[0].replace('"', "")
#print bullet_button_id
rte_button_link_id = "rte-button-link"
destination_id = "weblink-destination"
link_browser_insert_id = "link-browser-insert"
rte_button_publish_id = "rte-button-publish"
weblink_panel_id = "weblink-panel-id"
search_panel_id = "search-panel-id"
link_search_text = "link-search-text"
search_panel_button = "search-panel-button"
confluence_link = "confluence-link"
time.sleep(4)
flag = False
#department_titles_existed_from_weekly_report = map(lambda x: x.replace("</a>", ""), re.findall('<a href=.*?>(' + title_week + '.*?</a>)',re.findall('(<ul><li><a.*?</a></li></ul>)', reduce(lambda x,y: x+y, content_week))[0]))
#department_titles_need_to_added = filter(lambda x: x not in department_titles_existed_from_weekly_report, department_titles)
try:
    department_titles_existed_from_weekly_report = map(lambda x: x.replace("</a>", ""), re.findall('<a href=.*?>(' + title_week + '.*?</a>)',re.findall('(<ul><li><a.*?</a></li></ul>)', reduce(lambda x,y: x+y, content_week))[0]))
    department_titles_need_to_added = filter(lambda x: x not in department_titles_existed_from_weekly_report, department_titles)
    if len(department_titles_need_to_added) == 0:
        print "no need to add department titles to the weekly report since already existed!"
except IndexError:
    department_titles_need_to_added = department_titles
    print "department reports is not added to weekly report!"
if len(department_titles_need_to_added) > 0:
    print department_titles_need_to_added
    driver.get(week_edit_url + "&" + params)
    time.sleep(4)
    for department_title in department_titles_need_to_added:
        if flag == True:
            driver.find_element_by_id("editPageLink").click()
            time.sleep(2)
        else:
            count = 0
            while remove_bullet(title_week) and count < 100:
                #print count
                if count == 0:
                    driver.find_element_by_id("tinymce").send_keys(Keys.CONTROL,'a')
                driver.switch_to.default_content()
                driver.find_element_by_id("rte-button-bullist").click()
                count += 1
        time.sleep(1)
        #print "1"
        driver.switch_to.default_content()
        driver.find_element_by_id(rte_button_link_id).click()
        time.sleep(1)
        driver.find_element_by_id(search_panel_id).click()
        time.sleep(1)
        driver.find_element_by_id(link_search_text).clear()
        time.sleep(1)
        driver.find_element_by_id(link_search_text).send_keys(department_title)
        time.sleep(1)
        driver.find_element_by_id(search_panel_button).click()
        time.sleep(1)
        tr_nodes = driver.find_elements_by_tag_name("tr")
        find = False
        for tr_node in tr_nodes:
            span_nodes = tr_node.find_elements_by_tag_name("span")
            if len(filter(lambda x: x == "MIE-CD" or x == department_title, map(lambda x: x.text, span_nodes))) == 2:
                print filter(lambda x: x == "MIE-CD" or x == department_title, map(lambda x: x.text, span_nodes))
                tr_node.find_element_by_class_name("title-field").click()
                find = True
                break
        if not find:
            print department_title  + " is not found!"
        time.sleep(1)
        for intert_button_tag in driver.find_elements_by_tag_name("button"):
            if intert_button_tag.get_attribute("id") == "link-browser-insert" and intert_button_tag.get_attribute("class") == "button-panel-button" and intert_button_tag.text == "Insert":
                print "OK"
                intert_button_tag.send_keys(Keys.ENTER)
                break
        if department_title == department_titles_need_to_added[-1]:
            time.sleep(1)
            driver.switch_to.frame("wysiwygTextarea_ifr")
            driver.find_element_by_id("tinymce").send_keys(Keys.CONTROL,'a')
            driver.switch_to.default_content()
            driver.find_element_by_id(bullet_button_id).click()
        time.sleep(1)
        driver.find_element_by_id(rte_button_publish_id).click()
        flag = True
driver.quit()
print "create weekly report is finished!"

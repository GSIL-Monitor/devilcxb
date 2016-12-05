# -*- coding: cp936 -*-
import xlrd
import os
from xml.dom.minidom import parse


class TranslateXml(object):
    def __init__(self, xml_based_foder, excel_file):
        self.lang_tables = {
            'CHINE_NEW': 'zh-rCN', # 简体中文
            'CHINE_OLD': 'zh-rHK', # 繁体中文
            'ENGLISH': 'en',     # 英语
            'FRENCH': 'fr',      # 法语
            'DUTCH': 'nl',       # 荷兰
            'GERMAN': 'de',      # 德国
            'GREEK': 'el',       # 希腊
            'HUNGARIAN': 'hu',   # 匈牙利
            'ITALIAN': 'it',     # 意大利
            'PORTUGUESE': 'pt',  # 葡萄牙
            'SPANISH': 'es',     # 西班牙
            'TURKISH': 'tr',     # 土耳其
            'POLISH': 'pl',      # 波兰
            'CZECH': 'cs',       # 捷克
            'MALAY': 'ms',       # 马来语
            'INDONESIAN': 'in',  # 印尼
            'SLOVAK': 'sk',      # 斯洛伐克
            'ROMANIAN': 'ro',    # 罗马尼亚
            'SLOVENIAN': 'sl',   # 斯洛文尼亚
            'THAI': 'th',        # 泰国
            'SERBIAN': 'sr',     # 塞尔维亚
            'GALICIAN': 'gl',    # 加利西亚
            'VIETNAMESE': 'vi',  # 越南
            'BRAZILIAN': 'pt-rBR', # 巴西
            'JAPANESE': 'ja',    # 日语
            'LATINESP': 'es-rLA',  # 拉丁西班牙语
            'FARSI': 'fa',        # 波斯
            'CROATIAN': 'hr',	# 克罗地亚
            'RUSSIAN': 'ru',	    # 俄语
            # IDOL3 与 MIE 差异
            'ARABIC': 'ar',            # 阿拉拍语
            'CATALAN': 'ca',           # 加泰罗尼亚
            'DANISH': 'da',            # 丹麦
            'FINNISH': 'fi',           # 芬兰
            'FRENCH_CA': 'fr-rCA',     # 法语-加拿大
            'NORWEGIAN': 'no',         # 挪威
            'SWEDISH': 'sv',           # 瑞典
            'EUSKERA': 'eu',           # 巴斯克
            # IDOL3 新增语言
            'ALBANIAN': 'sq',          # 阿尔巴尼亚文
            'BENGALI': 'bn-rBD',       # 孟加拉
            'BULGARIAN': 'bg',         # 保加利亚语
            'CAMBODIAN': 'km-rKH',     # 柬埔寨
            'ESTONIAN': 'et',          # 爱沙尼亚语
            'HEBREW': 'he',            # 希伯来语
            'KOREAN': 'ko',            # 朝鲜语
            'LAOTIAN': 'lo-rLA',       # 老挝语
            'LATVIAN': 'lv',           # 拉脱维亚语
            'LITHUANIAN': 'lt',        # 立陶宛
            'MACEDONIAN': 'mk',        # 马其顿
            'MYANMAR': 'my-rMM',       # 缅甸
            'UKRAINIAN': 'uk',         # 乌克兰语
            'URDU': 'ur',              #乌拉都
            'HINDI': 'hi-rIN'          #印地语
        }
        self.base_folder = xml_based_foder
        wb = xlrd.open_workbook(excel_file)
        self.sheet = wb.sheet_by_index(0)
        self.refNames = map(lambda x: x.split(":")[-1], self.sheet.col_values(0)[1:])

    def languages_from_excel(self):
        return map(lambda x: str(x.value.upper()), self.sheet.row(0)[1:])

    def languages_from_defined(self):
        return map(lambda x: x.upper(), self.lang_tables.keys())

    def values_from_excel(self, language):
        values = {}
        translations = self.sheet.col_values(map(lambda x: x.upper(), self.sheet.row_values(0)).index(language))[1:]
        for refName in self.refNames:
            #print translation
            values[refName] = translations[self.refNames.index(refName)].strip()
        return values

    def values_from_xml(self, file_path):
        values = {}
        doc = parse(file_path)
        strings = doc.getElementsByTagName("string")
        for refName in self.refNames:
            for string in strings:
                if string.getAttribute("name") == refName:
                    for child_node in string.childNodes:
                        if child_node.nodeType == 3:
                            values[refName] = child_node.nodeValue
        return values

    def check_result(self, values_from_xml, values_from_excel, language, file_path = None):
        for key in values_from_xml.keys():
            flag = False
            if "&gt;" in values_from_xml[key]:
                values_from_xml[key] = values_from_xml[key].replace("&gt;", ">")
            if "&lt;" in values_from_xml[key]:
                values_from_xml[key] = values_from_xml[key].replace("&gt;", "<")
            if "\\" in values_from_xml[key]:
                values_from_xml[key] = values_from_xml[key].replace("&quot;", "")
                flag = True
            if values_from_excel[key][0] == '"' and values_from_excel[key][-1] == '"':
                if flag:
                    values_from_xml[key] = '"' + values_from_xml[key] + '"'
                else:
                    values_from_xml[key] = '"' + values_from_xml[key][1: -1] + '"'
        if values_from_xml == values_from_excel:
            print "check " + language + " is passed!"
        else:
            print "check " + language + " is failed, please check the details as below:"
            print "values_from_xml:"
            print "path is " + file_path
            # print values_from_xml.keys()
            # print values_from_excel.keys()
            for key in filter(lambda x:values_from_excel[x] != values_from_xml[x], values_from_xml):
                print key + ":"
                print values_from_xml[key].encode("utf-8")
            print "values_from_excel:"
            for key in filter(lambda x:values_from_xml[x] != values_from_excel[x], values_from_excel):
                print key + ":"
                print values_from_excel[key].encode("utf-8")

    def main(self):
        languages_from_excel = self.languages_from_excel()
        languages_from_defined = self.languages_from_defined()
        if len(filter(lambda x: x in languages_from_defined, languages_from_excel)) == len(languages_from_excel):
            print "all languages are existed in excel, check is passed!"
        else:
            print filter(lambda x: x not in languages_from_defined, languages_from_excel)
        if len(filter(lambda x: os.path.isdir(os.path.join(self.base_folder, "values-" + self.lang_tables[x])) and os.path.isfile(os.path.join(self.base_folder, "values-" + self.lang_tables[x]) + "\\" + "strings.xml"), languages_from_excel)) == len(languages_from_excel):
            print "all strings.xml file and corresponding folder are existed!"
        else:
            print "the below languages are missed from xml files:"
            print filter(lambda x: not os.path.isdir(os.path.join(self.base_folder, "values-" + self.lang_tables[x])) or not os.path.isfile(os.path.join(self.base_folder, "values-" + self.lang_tables[x]) + "\\" + "strings.xml"), languages_from_excel)
            for item in filter(lambda x: not os.path.isdir(os.path.join(self.base_folder, "values-" + self.lang_tables[x])) or not os.path.isfile(os.path.join(self.base_folder, "values-" + self.lang_tables[x]) + "\\" + "strings.xml"), languages_from_excel):
                del languages_from_excel[languages_from_excel.index(item)]
        for language in languages_from_excel:
            values_from_xml = self.values_from_xml(os.path.join(self.base_folder, "values-" + self.lang_tables[language]) + "\\" + "strings.xml")
            for key in values_from_xml.keys():
                if "'" in values_from_xml[key]:
                    if values_from_xml[key][0] != '"' or values_from_xml[key][-1] != '"':
                        print 'string is not start and end with "' + " and language is " + language + ", please check " + os.path.join(self.base_folder, "values-" + self.lang_tables[language]) + "\\" + "strings.xml ", " for key " + key
                    else:
                        values_from_xml[key] = values_from_xml[key][1:-1]
                    values_from_xml[key] = values_from_xml[key]
            values_from_excel = self.values_from_excel(language)
            self.check_result(values_from_xml, values_from_excel, language, os.path.join(self.base_folder, "values-" + self.lang_tables[language]) + "\\" + "strings.xml")

if __name__ == "__main__":
    xml_based_foder = r"C:\Users\xinjiu.qiao\Desktop\res"
    excel_file = r"C:\Users\xinjiu.qiao\Desktop\User Care_Translations_Swedish Proofreading 20160613.xlsx"
    TranslateXml = TranslateXml(xml_based_foder, excel_file)
    TranslateXml.main()
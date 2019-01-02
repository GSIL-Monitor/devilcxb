# -*- coding: cp936 -*-
import xlrd
import os
from xml.dom.minidom import parse
import re
import sys
import chardet


class TranslateJs(object):
    def __init__(self):
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
        }
        self.js_file = r"D:\Project\UserCare\v1.7.0\多语言测试\nps\output.js"
        wb = xlrd.open_workbook(r"D:\Project\UserCare\v1.7.0\多语言测试\UserCareV1.7.0_20160203.xlsx")
        self.sheet = wb.sheet_by_index(1)
        self.refNames = self.sheet.col_values(0)[1:]

    def languages_from_excel(self):
        return map(lambda x: str(x.value.upper()), self.sheet.row(0)[1:])

    def languages_from_defined(self):
        return map(lambda x: x.upper(), self.lang_tables.keys())

    def values_from_excel(self, language):
        values = {}
        translations = self.sheet.col_values(map(lambda x: x.upper(), self.sheet.row_values(0)).index(language))[1:5]
        for translation in translations:
            values[self.refNames[translations.index(translation)]] = translation.strip()
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

    def read_and_format_js(self):
        return eval(re.findall("{.*}", reduce(lambda x, y: x.strip() + y, open(self.js_file).readlines()))[0])

    def check_refNames(self,values):
        # print self.refNames
        # print values.keys()
        if len(filter(lambda x: x in values.keys(), self.refNames)) == len(self.refNames):
            return True
        else:
            print str(filter(lambda x: x not in values.keys(), self.refNames)) + " is missed from js file!"
            return False

    def check_languages_codes(self, languages_codes_for_excel, values):
        for refName in self.refNames:
            # print refName
            # print languages_codes_for_excel
            # print map(lambda x: x.upper(), values[refName].keys())
            if len(filter(lambda x: x in map(lambda x: x.upper(), values[refName].keys()), languages_codes_for_excel)) == len(languages_codes_for_excel):
                print "check languages codes for " + refName + " is passed!"
            else:
                print "check languages codes for " + refName + " is failed!"
                print "please check the informations: " + str(filter(lambda x: x not in map(lambda x: x.upper(), values[refName].keys()), languages_codes_for_excel))
                sys.exit(1)

    def check_result(self, values, languages_from_excel, languages_codes_for_excel):
        for refName in self.refNames:
            values_from_excel = {}
            count = 0
            while count < len(languages_from_excel):
                values_from_excel[self.lang_tables[languages_from_excel[count]].upper()] = self.sheet.cell_value(self.refNames.index(refName) + 1, count + 1).encode("utf-8")
                count += 1
            #print values_from_excel
            values_from_js = {}
            for key in values[refName].keys():
                if key.upper() in languages_codes_for_excel:
                    values_from_js[key.upper()] =  values[refName][key]
            #print values_from_js
            if values_from_excel == values_from_js:
                print "value is ckecked passed for " + refName + "!"
            else:
                print "values is checked failed for " + refName + "!"
                different_value_keys = filter(lambda x: values_from_excel[key] != values_from_js[key], values_from_excel.keys())
                print different_value_keys
                for key in different_value_keys:
                    print key + ":" + values_from_excel[key] + " " + values_from_js[key]
                sys.exit(1)

    def main(self):
        values = self.read_and_format_js()
        # print self.read_and_format_js()
        # print type(self.read_and_format_js())
        if self.check_refNames(values):
            print "check refNames is passed!"
        else:
            print "check refNames is failed!"
            sys.exit(1)
        languages_from_excel = self.languages_from_excel()
        languages_codes_for_excel = []
        for language_from_excel in languages_from_excel:
            languages_codes_for_excel.append(self.lang_tables[language_from_excel].upper())
        self.check_languages_codes(languages_codes_for_excel, values)
        self.check_result(values, languages_from_excel, languages_codes_for_excel)

if __name__ == "__main__":
    TranslateJs = TranslateJs()
    TranslateJs.main()
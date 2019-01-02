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
            'CHINE_NEW': 'zh-rCN', # ��������
            'CHINE_OLD': 'zh-rHK', # ��������
            'ENGLISH': 'en',     # Ӣ��
            'FRENCH': 'fr',      # ����
            'DUTCH': 'nl',       # ����
            'GERMAN': 'de',      # �¹�
            'GREEK': 'el',       # ϣ��
            'HUNGARIAN': 'hu',   # ������
            'ITALIAN': 'it',     # �����
            'PORTUGUESE': 'pt',  # ������
            'SPANISH': 'es',     # ������
            'TURKISH': 'tr',     # ������
            'POLISH': 'pl',      # ����
            'CZECH': 'cs',       # �ݿ�
            'MALAY': 'ms',       # ������
            'INDONESIAN': 'in',  # ӡ��
            'SLOVAK': 'sk',      # ˹�工��
            'ROMANIAN': 'ro',    # ��������
            'SLOVENIAN': 'sl',   # ˹��������
            'THAI': 'th',        # ̩��
            'SERBIAN': 'sr',     # ����ά��
            'GALICIAN': 'gl',    # ��������
            'VIETNAMESE': 'vi',  # Խ��
            'BRAZILIAN': 'pt-rBR', # ����
            'JAPANESE': 'ja',    # ����
            'LATINESP': 'es-rLA',  # ������������
            'FARSI': 'fa',        # ��˹
            'CROATIAN': 'hr',	# ���޵���
            'RUSSIAN': 'ru',	    # ����
            # IDOL3 �� MIE ����
            'ARABIC': 'ar',            # ��������
            'CATALAN': 'ca',           # ��̩������
            'DANISH': 'da',            # ����
            'FINNISH': 'fi',           # ����
            'FRENCH_CA': 'fr-rCA',     # ����-���ô�
            'NORWEGIAN': 'no',         # Ų��
            'SWEDISH': 'sv',           # ���
            'EUSKERA': 'eu',           # ��˹��
            # IDOL3 ��������
            'ALBANIAN': 'sq',          # ������������
            'BENGALI': 'bn-rBD',       # �ϼ���
            'BULGARIAN': 'bg',         # ����������
            'CAMBODIAN': 'km-rKH',     # ����կ
            'ESTONIAN': 'et',          # ��ɳ������
            'HEBREW': 'he',            # ϣ������
            'KOREAN': 'ko',            # ������
            'LAOTIAN': 'lo-rLA',       # ������
            'LATVIAN': 'lv',           # ����ά����
            'LITHUANIAN': 'lt',        # ������
            'MACEDONIAN': 'mk',        # �����
            'MYANMAR': 'my-rMM',       # ���
            'UKRAINIAN': 'uk',         # �ڿ�����
        }
        self.js_file = r"D:\Project\UserCare\v1.7.0\�����Բ���\nps\output.js"
        wb = xlrd.open_workbook(r"D:\Project\UserCare\v1.7.0\�����Բ���\UserCareV1.7.0_20160203.xlsx")
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
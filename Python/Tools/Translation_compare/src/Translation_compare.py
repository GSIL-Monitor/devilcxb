# -*- coding: utf-8 -*-
# Create by Hawkzy 2015-1
#   V1.1 Add function for multi-row with the same Eng-String
#   v1.2 2015-4-1 Add func of replacing <> with {{}} and if there are blanks in
#          it, they will be replace with _
#   v1.3 2015-4-2 support add <a ...> <xxx> </a> for <group name> and <username>
#          and fix a bug caused by split properties file using '='.
#   v2.0 2015-5-19 rewrite whole script, 
#           - use dict replace list, 
#           - def func to simplify process,
#           - add debug model.
#   v2.1 2015-5-21 
#           - fix a bug in 'replaceStr', if Ls==0, return s.replace() instead of s.
#           - add mismatch.txt to save the result of mismatch string.

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(sys.path[0]+'\\..\\lib')

from xlrd import open_workbook
from xlwt import *
import ConfigParser as cparser


class Translation_compare:

    def __init__(self):
        self.mismatch_file = ''
        self.result_excel = ''
        self.missID_file = ''
        self.languages_cnfinfo = self.get_languages_cnfinfo()

    def get_languages_cnfinfo(self):
        """
        获取翻译文件，以及properties文件路径等配置信息
        :return:
        """
        config = cparser.ConfigParser()
        config.read('..\\conf\\languages.ini')
        if 'languages' not in config.sections():
            return None
        file_path_options = config.options('file_path')
        properties_file_path = {}

        self.mismatch_file = config.get('result_file_path', 'mismatch_file')
        self.result_excel = config.get('result_file_path', 'result_excel')
        self.missID_file = config.get('result_file_path', 'missID_file')
        for option in file_path_options:
            properties_file_path[option] = config.get('file_path', option)

        languages = {'translation_file': config.get('languages', 'translation_file'),
                     'list_languages': str(config.get('languages', 'languages')).split(';'),
                     'properties_file_path': properties_file_path}
        return languages

    def read_language_excel(self, sheet_name='Sheet2'):
        """
        读取翻译文件的excel，将excel内容读取为{language：{key：value}}
        :return:每种语言key对应的翻译字典{language：{key：value}}，重复翻译的key，重复翻译的语言
        """
        translation_file = str(self.languages_cnfinfo.get('translation_file'))
        if translation_file is None or translation_file == '':
            return {}
        list_languages = self.languages_cnfinfo.get('list_languages')  # 语言list

        wb = open_workbook(translation_file)  # 打开excel文件，赋值给一个对象，便于后续对该对象进行操作
        targetSheet = wb.sheet_by_name(sheet_name)
        if targetSheet is None:
            return {}
        cols = targetSheet.ncols  # 翻译文件的列数
        rows = targetSheet.nrows  # 翻译文件的行数
        language_dict = {}  # 语言对应翻译字典
        key_repeat_dict = {}  # key出现大于等于2次的字典
        language_repeat_dict = {}  # 列中一种语言出现大于等于2次的字典
        for language in list_languages:
            key_value_dict = {}
            for col_index in range(cols):
                language_value = targetSheet.cell(0, col_index)
                language_appear_count = 1
                if language_value and language_value.value.upper() == language.upper():
                    if language_dict.has_key(language.upper()):  # 语言对应翻译字典中出现过，说明该语言又重复出现
                        language_appear_count += 1
                        language_repeat_dict[language.upper()] = language_appear_count
                    else:
                        key_appear_count = 1
                        for row_index in range(1, rows):
                            key = str(targetSheet.cell(row_index, 0).value).split(':')[-1].strip().strip('\n')
                            value = str(targetSheet.cell(row_index, col_index).value).strip().strip('\n')
                            if key_value_dict.has_key(key):  # 可以对应翻译字典中出现过，说明该key又重复出现
                                key_appear_count += 1
                                key_repeat_dict[key] = key_appear_count
                            key_value_dict[key] = value
            language_dict[language.lower()] = key_value_dict

        return language_dict, key_repeat_dict, language_repeat_dict

    def get_compare_result(self, language_resource_file_Dict={}, right_language_dict={}, repeat_dict={}):
        """
        对比excel文件中的翻译和properties文件是否一致
        :param language_resource_file_Dict: properties文件的翻译字典
        :param right_language_dict: excel文件中的翻译字典
        :param repeat_dict: 重复出现的字典
        :return:
        """
        mis_match_file = open(self.mismatch_file, 'w')
        misskey = open(self.missID_file, 'w')
        list_result = []
        try:
            if language_resource_file_Dict is None or len(language_resource_file_Dict) == 0 \
                    or right_language_dict is None or len(right_language_dict) == 0:
                return list_result
            excel_key_list = []
            for language in right_language_dict.keys():
                excel_key_list = right_language_dict.get(language).keys()
                break
            for key in excel_key_list:
                match_suc = ''
                match_fail = ''
                mis_match = ''
                for language in right_language_dict.keys():
                    if language_resource_file_Dict.get(language).has_key(key):
                        if language_resource_file_Dict.get(language).get(key) == \
                                right_language_dict.get(language).get(key):
                            match_suc += language + ';'
                        else:
                            match_fail += language + ';'
                            mis_match_file.write('language[%s] key[%s]: \n excel:           %s\n'
                                                 ' properties_file: %s \n\n' %
                                                 (language, key, right_language_dict.get(language).get(key),
                                                  language_resource_file_Dict.get(language).get(key)))
                    else:
                        mis_match += language + ';'
                result_dict = {'match_suc': match_suc,
                               'match_fail': match_fail,
                               'mis_match': mis_match,
                               'key': key}
                if key in repeat_dict:
                    result_dict['repeat_count'] = repeat_dict.get(key)
                list_result.append(result_dict)

            for language in language_resource_file_Dict.keys():
                mis_excel = 'in excel language[%s] mis key:\n' % language
                for key in language_resource_file_Dict.get(language).keys():
                    if right_language_dict.get(language).has_key(key):
                        continue
                    else:
                        mis_excel += key + ' \n'
                misskey.write(mis_excel+'\n')
        except:
            print 'compare error'
        finally:
            mis_match_file.close()
            misskey.close()

        return list_result

    def readProperties(self, filename):
        """
        读取properties文件，如果不存在返回空对象
        如果存在返回每一行为元素的list，每行去掉两头的空格和特殊字符
        :param filename: properties文件路径
        :return:
        """
        if not (os.path.isfile(filename)):  # 判断参数filename是不是文件
            print filename + ' not exist!!!'  # 如果不是文件，则，打印结果并退出
            return []
        else:
            f = open(filename, 'r')
            lines = f.readlines()
            for index, line in enumerate(lines):
                line = line.strip()  # 对line元素，去掉两头的空格和特殊字符。
                lines[index] = line
            f.close()
        return lines

    def get_resource_file_Dict(self, filename):
        """
        解析properties文件的每行的内容，将每行以第一个‘=’进行拆分,
        拆分后以key：value的形式保存在字典中
        :param filename: properties文件路径
        :return: 返回拆分后的字典对象
        """
        lines = self.readProperties(filename)
        properties_key_valuse_dt = {}
        # misskey = open(self.missID_file, 'a')
        for lineNum, line in enumerate(lines):  # 在列表lines中遍历
            key_value = line.split('=', 1)  # 以第一个=拆分每行（“等号前的值”，’等号后的值‘）
            # if len(key_value) != 2:  # 如果没有=，则不进行拆分，直接存放在key_value中。key_value的长度则不等于2
            #     misskey.write(filename.split('\\')[-1] + ' has error line: ' + str(lineNum + 1) + '\n')
            # else:
            properties_key_valuse_dt[key_value[0].strip()] = key_value[1].strip()
        # misskey.close()
        return properties_key_valuse_dt

    def get_language_resource_file_Dict(self, properties_File_names):
        """
        获取语言对应properties文件拆分后的字典对象：
        返回对象为{language：{key：value}}
        :param properties_File_names: 资源文件列表
        :return:
        """
        tmpDict = {}
        for key in properties_File_names:
            targetDict = self.get_resource_file_Dict(properties_File_names[key])
            tmpDict[key] = targetDict  # 将对应语言的properties拆分对象存放在字典中
        return tmpDict

    def save_Result_2_Excel(self, dict_Cmp_Result, excelResult_file):
        wb = Workbook(encoding='utf-8')
        ws = wb.add_sheet('result')

        # write the first row, which are title of data
        ws.write(0, 0, 'Key')
        ws.write(0, 1, 'Match Language')
        ws.write(0, 2, 'Failed Language')
        ws.write(0, 3, 'Miss Language')
        ws.write(0, 4, 'Redundant Times')  # 设置标题，存放重复的次数

        # write the compare result to sheet
        for index in range(len(dict_Cmp_Result)):
            ws.write(index + 1, 0, dict_Cmp_Result[index].get('key'))
            ws.write(index + 1, 1, dict_Cmp_Result[index].get('match_suc'))
            ws.write(index + 1, 2, dict_Cmp_Result[index].get('match_fail'))
            ws.write(index + 1, 3, dict_Cmp_Result[index].get('mis_match'))
            ws.write(index + 1, 4, dict_Cmp_Result[index].get('repeat_count'))
        wb.save(excelResult_file)
        print "done!!!!!"

    def replaceStr(self, s):
        # Ls = re.findall('<[^<,^>]*>', s)
        # if len(Ls) == 0:
        #     return s.replace('\n','<br />')
        # else:
        #     for l in Ls:
        #
        #         l1=l.replace(' ', '_').replace('<', '{{').replace('>', '}}')
        #         if l1 == '{{group_name}}':
        #             l1 = '<a class="group-ref">' + l1 + '</a>'
        #         elif l1 == '{{username}}':
        #             l1 = '<span class="who">' + l1 + '</span>'
        #         s = s.replace(l, l1 )
        #     return s.replace('\n','<br />')
        return s

    def excu_cmp(self):
        """
        执行对比的入口
        """
        language_resource_file_Dict = self.get_language_resource_file_Dict(
            self.languages_cnfinfo.get('properties_file_path'))
        right_language_dict, key_repeat_dict, language_repeat_dict = self.read_language_excel()
        list_result = self.get_compare_result(language_resource_file_Dict, right_language_dict, key_repeat_dict)
        self.save_Result_2_Excel(list_result, self.result_excel)


if __name__ == '__main__':
    instance = Translation_compare()
    instance.excu_cmp()

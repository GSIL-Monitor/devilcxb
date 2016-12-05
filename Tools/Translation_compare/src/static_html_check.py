# -*- coding: cp936 -*-
import urllib2
import urllib
from selenium import webdriver


params ={
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
"""
for key in params.keys():
    print key
    param = urllib.urlencode({"language": params["CHINE_NEW"]})
    print param
    url = "file:///C:/Jenkins/workspace/UserCare_code_apk_generation/UserCare/assets/staticnps/survey.html"
    req = urllib2.Request(url, param) 
    res = urllib2.urlopen(req)
    print res.read()
"""
driver = webdriver.Firefox(timeout=30)
url = "file:///C:/Jenkins/workspace/UserCare_code_apk_generation/UserCare/assets/staticnps/survey.html"
for key in params.keys():
    param = urllib.urlencode({"language": params[key]})
    driver.get(url + "?" + param)
    try:
        driver.find_element_by_class_name("start_wrap")
        print key + " is tested passed!"
    except:
        print key + " is tested failed!"
        print "please check the url manually!"
        print url + "?" + param
    
driver.quit()

# -*- coding: cp936 -*-
import urllib2
import urllib
from selenium import webdriver


params ={
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

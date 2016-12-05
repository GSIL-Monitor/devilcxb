import os
import re

root_path_12 = r"\\cdapp01\MIE-CD\02_Validation\06_Temp\Thirdapp\app_center\2015-12-12"
list_12 = os.listdir(root_path_12)
#print len(list_12)
list_12 = filter(lambda x: re.search(".*\.apk$", x), list_12)
print len(list_12)

root_path_14 = r"\\cdapp01\MIE-CD\02_Validation\06_Temp\Thirdapp\app_center\2015-12-14"
list_14 = os.listdir(root_path_14)
list_14 = filter(lambda x: re.search(".*\.apk$", x), list_14)
print len(list_14)

print len(filter(lambda x: x not in list_12, list_14))
print len(filter(lambda x: x in list_12, list_14))

for i in filter(lambda x: x not in list_12, list_14):
    print i.replace(".apk", "")

import urllib2
import re
import urllib
import os

# contents = urllib2.urlopen("http://mp.weixin.qq.com/s/rK6nB9rrvet9zOrZ3n09YA").read()
# image_urls = set(re.findall('data-src="(https://mmbiz.qpic.cn/mmbiz_jpg/.*?)"', contents))
# count = 1
# for image_url in image_urls:
#     print image_url
#     urllib.urlretrieve(image_url, os.path.join(r"C:\Users\Sunny\Desktop\test", "{}.jpg".format(count)))
#     count += 1


from PIL import Image
import pytesseract

src_path = r"C:\Users\Sunny\Desktop\test"
images = os.listdir(src_path)
count = 0
numbers = []
for image in images:
    print image
    image_object = Image.open(os.path.join(src_path, image))
    code = pytesseract.image_to_string(image_object)
    for i in code.split("\n"):
        if "B4400" in i or "B3586" in i:
            count += 1
            numbers.append(i + " " + image)
    if count == 2:
        break

for i in numbers:
    print i
from xml.etree.ElementTree import ElementTree,Element

tree = ElementTree()
tree.parse("AndroidManifest.xml")
nodes = tree.findall("application/meta-data")
write_flag = False
for node in nodes:
    keys = node.attrib.keys()
    for key in keys:
        if "name" in key and node.attrib[key] == "APP_FOR_HD":
            #print node.attrib[keys[keys.index(key)-1]]
            node.attrib[keys[keys.index(key)-1]] = "1"
            write_flag = True
            break
node = tree.find("application")
keys = node.attrib.keys()
for key in keys:
    if "label" in key and "@string/app_name" in node.attrib[key] and "@string/app_name" == node.attrib[key]:
        node.attrib[key] = "@string/app_name" + "_hd"
        write_flag = True
        break
if write_flag == True:
    tree.write("AndroidManifest.xml")
class RobotFrameworkTool(object):
    def __init__(self):
        pass

    def convertVaribleFromPythontoRobot(self, value, parameter_name, used_once = True, result = {}):
        if used_once:
            pass
        else:
            result = {}
            used_once = True
        if type(value) == dict:
            flag = False
            for item in value:
                if type(value[item]) == dict:
                    self.convertVaribleFromPythontoRobot(value[item], "&" + parameter_name[1:] + "_dict_" + str(value.keys().index(item)), used_once, result)
                elif type(value[item]) == list:
                    self.convertVaribleFromPythontoRobot(value[item], "@" + parameter_name[1:] + "_list_" + str(value.keys().index(item)), used_once, result)
                else:
                    flag = True
            if flag:
                result[parameter_name] = reduce(lambda x, y: str(x) + " " + str(y) + "=" + str(value[y]), value, "")
                # print parameter_name,
                # print reduce(lambda x, y: str(x) + " " + str(y) + "=" + str(value[y]), value, "")
        elif type(value) == list:
            flag = False
            for item in value:
                if type(item) == dict:
                    self.convertVaribleFromPythontoRobot(item, "&" + parameter_name[1:] + "_dict_" + str(value.index(item)), used_once, result)
                elif type(item) == list:
                    self.convertVaribleFromPythontoRobot(item, "@" + parameter_name[1:] + "_list_" + str(value.index(item)), used_once, result)
                else:
                    if not flag:
                        flag = True
            if flag:
                result[parameter_name] = reduce(lambda x, y: str(x) + " " + str(y), value, "")
                # print parameter_name,
                # print reduce(lambda x, y: str(x) + " " + str(y), value, "")
        return result

if __name__ == "__main__":
    test = RobotFrameworkTool()
    a = [{'contentUrl': 'https://www.baidu.com1', 'status': 'Y', 'updateTime': 1459302866000L, 'name': 'banner5', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160324/17/11/33/6Cr0VKIFG5.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459302881000L, 'id': 47}, {'contentUrl': 'www.baidu.com', 'status': 'Y', 'name': 'banner4', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160328/10/15/32/MwnuXfBI8F.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459131324000L, 'id': 48}, {'contentUrl': 'http://www.baidu.com', 'status': 'Y', 'updateTime': 1459407038000L, 'name': '5555', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160323/13/57/43/oPdcqOm34R.jpg', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459407054000L, 'id': 50}, {'contentUrl': 'fds', 'status': 'Y', 'name': 'fd', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160328/15/31/36/jTDekjtDOW.jpg', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459150282000L, 'id': 51}, {'contentUrl': 'http://www.baidu.com', 'status': 'Y', 'name': 'test1', 'position': 1, 'imageUrl': '/boss/static//images/loading.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459240231000L, 'id': 54}]
    b = {'contentUrl': 'https://www.baidu.com', 'status': 'Y', 'updateTime': 1459302866000L, 'name': 'banner5', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160324/17/11/33/6Cr0VKIFG5.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459302881000L, 'id': 47}
    c = [1, 2, 3, 4]
    d = [[1, 2, 3, 4], [1, 3, 3, 4], [1, 2, 4, 4], [1, 1, 3, 4]]
    e = {"status": "Y", "code": 200, "items": [{'contentUrl': 'https://www.baidu.com', 'status': 'Y', 'updateTime': 1459302866000L, 'name': 'banner5', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160324/17/11/33/6Cr0VKIFG5.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459302881000L, 'id': 47}, {'contentUrl': 'www.baidu.com', 'status': 'Y', 'name': 'banner4', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160328/10/15/32/MwnuXfBI8F.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459131324000L, 'id': 48}, {'contentUrl': 'http://www.baidu.com', 'status': 'Y', 'updateTime': 1459407038000L, 'name': '5555', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160323/13/57/43/oPdcqOm34R.jpg', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459407054000L, 'id': 50}, {'contentUrl': 'fds', 'status': 'Y', 'name': 'fd', 'position': 1, 'imageUrl': 'http://dl.cc.tclclouds.com/swift/v1/fzl_container/usercare/20160328/15/31/36/jTDekjtDOW.jpg', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459150282000L, 'id': 51}, {'contentUrl': 'http://www.baidu.com', 'status': 'Y', 'name': 'test1', 'position': 1, 'imageUrl': '/boss/static//images/loading.gif', 'mnc': 'D4460', 'mcc': 'D4460', 'createTime': 1459240231000L, 'id': 54}]}
    result = test.convertVaribleFromPythontoRobot(a, "@item_defined")
    for item in sorted(result.keys()):
        print item, result[item]
    print "@item_defined" + " " + reduce(lambda x, y: x + " " + y, sorted(result.keys()))
    result = test.convertVaribleFromPythontoRobot(b, "&item_defined", used_once=False)
    for item in sorted(result.keys()):
        print item, result[item]
    result = test.convertVaribleFromPythontoRobot(c, "@item_defined", used_once=False)
    for item in sorted(result.keys()):
        print item, result[item]
    result = test.convertVaribleFromPythontoRobot(d, "@item_defined", used_once=False)
    for item in sorted(result.keys()):
        print item, result[item]
    print "@item_defined" + " " + reduce(lambda x, y: x + " " + y, sorted(result.keys()))
    result = test.convertVaribleFromPythontoRobot(e, "&item_defined", used_once=False)
    for item in sorted(result.keys()):
        print item, result[item]
    print "&item_defined" + " " + reduce(lambda x, y: x + " " + y, sorted(result.keys()))

from robot_test.Common.printTxt import printTxt as new


class class_1(object):
    def __init__(self):
        pass

    def run(self):
        printTxt = new("run test1")
        printTxt.printrun()

    def test(self):
        print "OK"

if __name__ == "__main__":
    test = class_1()
    test.run()
    test.test()
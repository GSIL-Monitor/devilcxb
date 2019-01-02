# -*- coding: utf-8 -*-

# 闭包主要用来保留当前的状态
def closure(param1):
    def inner_function(param2):
        print "{}, {}".format(param1, param2)
    return inner_function

if __name__ == '__main__':
    test = closure("Good morning") # 调用closure方法，返回inner_function函数
    test("Mike") #调用inner_function函数
    test("Rachel") # inner_function函数
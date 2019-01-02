# -*- coding: utf-8 -*-
"""
可以用在 for 语句进行循环的对象就是可迭代对象。除了内置的数据类型（列表、元组、字符串、字典等）可以通过 for 语句进行迭代，
我们也可以自己创建一个容器，包含一系列元素，可以通过 for 语句依次循环取出每一个元素，这种容器就是迭代器（iterator）。
除了用 for 遍历，迭代器还可以通过 next() 方法逐一读取下一个元素。要创建一个迭代器有3种方法，其中前两种分别是：
1. 为容器对象添加 __iter__() 和 __next__() 方法（Python 2.7 中是 next()）；__iter__() 返回迭代器对象本身 self，__next__()
   则返回每次调用 next() 或迭代时的元素；
2. 内置函数 iter() 将可迭代对象转化为迭代器
3. 生成器（generator）通过yield返回
"""
# demo 1
print iter([1, 2, 3])


# demo 2
class Container(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        print("[LOG] I made this iterator!")
        return self

    def next(self):  # python3请用__next__(self):
        if self.start < self.end:
            i = self.start
            self.start += 1
            return i
        else:
            raise StopIteration()


if __name__ == '__main__':

    c = Container(0, 5)
    print c
    for i in c:
        print i


# demo 3
def test(lists):
    for i in lists:
        yield i


iterator = (i for i in range(5))
a = test(iterator)
for i in a:
    print i

# -*- coding: utf-8 -*-
"""
使用模块: 本实例不做单独展示，Python 的模块引用就是天然的单例模式， 因为第一次引用会生成.pyc, 第二次会自动加载.pyc
使用 __new__
使用装饰器（decorator）
使用元类（metaclass）
"""
# demo 1


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class A(Singleton):
    a = 1


if __name__ == '__main__':
    a = A()
    b = A()
    print id(a), id(b)

# demo 2
from functools import wraps


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances

    return get_instance


@singleton
class A():
    a = 1


if __name__ == '__main__':
    a = A()
    b = A()
    print id(a), id(b)


# demo 3
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class A(object):
    __metaclass__ = Singleton


if __name__ == '__main__':
    a = A()
    b = A()
    print id(a), id(b)

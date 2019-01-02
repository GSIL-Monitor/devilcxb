import sys


# demo 1
def decorator(f):
    print "function of {} is start to executed!".format(f.func_name)
    f()
    print "function of {} is end to executed!".format(f.func_name)


@decorator  # similar to decorator(test)
def test():
    print "function {} is executing!".format(sys._getframe().f_code.co_name)


# demo 2
import logging


def use_logging(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if level == 'warning':
                logging.warning("function {} is executing!".format(sys._getframe().f_code.co_name))
            return func(*args, **kwargs)

        return wrapper

    return decorator


@use_logging("warning")
def test(name='foo'):
    print("i am %s" % name)


test("test")

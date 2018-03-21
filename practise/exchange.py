def iteraction(func):
    def wrapper(*args, **kw):
        print "start to call " + func.__name__
        result = func(*args, **kw)
        print "end to call " + func.__name__
        return result
    return wrapper

class Exchange(object):
    def __init__(self, int_a, int_b):
        self.a = int_a
        self.b=int_b

    @iteraction
    def run(self):
        """
        action to exchange two value
        :return: tuple result
        """
        self.b = self.a + self.b
        self.a = self.b - self.a
        self.b = self.b - self.a
        return self.a, self.b

if __name__ == '__main__':
    exchange = Exchange(1, 2)
    print exchange.run()
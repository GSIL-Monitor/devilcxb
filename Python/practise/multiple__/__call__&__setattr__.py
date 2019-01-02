class MyClass(dict):
    def __init__(self):
        pass

    def __call__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

if __name__ == '__main__':
    Test = MyClass()
    Test.a = 1
    print Test("a")
    print Test["a"]
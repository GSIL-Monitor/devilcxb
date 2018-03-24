# -*-coding:UTF-8-*-

"""
工厂模式有一种非常形象的描述，建立对象的类就如一个工厂，而需要被建立的对象就是一个个产品；
在工厂中加工产品，使用产品的人，不用在乎产品是如何生产出来的。从软件开发的角度来说，这样就有效的降低了模块之间的耦合。

简单工厂的作用是实例化对象，而不需要客户了解这个对象属于哪个具体的子类。简单工厂实例化的类具有相同的接口或者基类，在子类比较固定并不需要扩展时，
可以使用简单工厂。如数据库生产工厂就是简单工厂的一个应用

采用简单工厂的优点是可以使用户根据参数获得对应的类实例，避免了直接实例化类，降低了耦合性；缺点是可实例化的类型在编译期间已经被确定，如果增加新类 型，
则需要修改工厂，不符合OCP（开闭原则）的原则。简单工厂需要知道所有要生成的类型，当子类过多或者子类层次过多时不适合使用。
"""


class Operation(object):
    def __init__(self, a=0, b=0):
        self.a = a
        self.b = b

    def get_result(self):
        pass


class Add(Operation):
    def get_result(self):
        return self.a + self.b


class Minus(Operation):
    def get_result(self):
        return self.a - self.b


class Muti(Operation):
    def get_result(self):
        return self.a * self.b


class divide(Operation):
    def get_result(self):
        try:
            return self.a / self.b
        except ZeroDivisionError:
            raise


class OperationFactory(object):
    def choose_operation(self, operation):
        if operation == "+":
            return Add()
        elif operation == "-":
            return Minus()
        elif operation == "*":
            return Muti()
        elif operation == "/":
            return divide()


if __name__ == '__main__':
    operation = OperationFactory()
    operation_object = operation.choose_operation("+")
    operation_object.a = 1
    operation_object.b = 2
    print operation_object.get_result()

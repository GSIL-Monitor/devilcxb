import a
import b

class d(object):
    def __init__(self,init,tn = None):
        if init:
            self.a = a.a()
            self.tn = self.a.tn
            print "init is finished!"
        else:
            self.tn = tn
            print "no need to init!"
        self.b = b.b()

    def test(self):
        self.tn.write(self.b.command3 + b'\n')
        result =self.tn.read_until(b'~$ ',10)
        return result.split("\r\n")
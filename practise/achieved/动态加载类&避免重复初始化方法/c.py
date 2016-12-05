import a
import b

class c(object):
    def __init__(self,init,tn = None):
        if init:
            self.a = a.a()
            self.tn = self.a.tn
            self.b = b.b()
            print "init is finished!"
        else:
            self.tn = tn
            print "no need to init!"

    def test(self):
        #print self.a.tn
        #print self.b.command
        self.tn.write(self.b.command1 + b'\n')
        result =self.tn.read_until(b'~$ ',5)
        print result.split("\r\n")
"""
if __name__ == "__main__":
    c = c()
    c.main()
"""
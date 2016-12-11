from subprocess import Popen, PIPE, STDOUT
p = Popen(['python', 'test1.py'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
print p.stdout.readline().rstrip()
print p.communicate('mike')[0].rstrip()
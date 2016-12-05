# -*- coding: cp936 -*-
import datetime
import threading
import time
import re

def nice_print(message, sign='*'):
    '''
        Printing nice banners
    '''
    print(''.join([' ', sign*len(message)]))
    print(''.join([' ', message]))
    print(''.join([' ', sign*len(message)]))
"""    
global test
def do_something(i):
    time.sleep(1)
    test.append(i)
    #open("test.txt", "a+").write("do something! " + str(i) + " times" + "\n")
  
# compare range and range with threading.
count = 5
# 计算range的时间。
start_time = time.time()
test = []
for i in range(count):
    do_something(i)
end_time = time.time()
range_time = end_time - start_time
nice_print(str(range_time))

# 使用threading计算range的时间。
start_time = time.time()
test = []
count_start = 0
count_end = 0
while count_end < len(range(count)):
    #print datetime.datetime.now()
    threads = []
    if count_start + 300 < len(range(count)):
        count_end =  count_start + 300
    else:
        count_end = len(range(count))
    for item in range(count)[count_start:count_end]:
        count += 1
        t = threading.Thread(target=do_something,args=(item,))
        #print t.getName()
        # 启动线程
        threads.append(t)
    for t in threads:
        #print time.ctime()
        t.start()
    # 等待子线程结束
    for t in threads:
        t.join()
    count_start += 300
    #print datetime.datetime.now()
end_time = time.time()
thread_xrange_time = end_time - start_time

nice_print(str(thread_xrange_time))

#compare range and xrange.
# range is removed for python 3.3 and xrange is used instead and renamed range.
count = 10000000
# 计算range的时间。
start_time = time.time()
test = []
for i in range(count):
    pass
end_time = time.time()
range_time = end_time - start_time
nice_print(str(range_time))

# 计算xrange的时间。
start_time = time.time()
test = []
for i in xrange(count):
    pass
end_time = time.time()
xrange_time = end_time - start_time
nice_print(str(xrange_time))
"""

"""    
#compare nomal for looping and lambda.
#normal
count = 10000000
start_time = time.time()
list_a = []
for i in range(count):
    list_a.append(i+1)
end_time = time.time()        
for_looping_time = end_time - start_time
nice_print(str(for_looping_time))
#print len(list_a)

#lambda
start_time = time.time()
list_a = []
list_a = map(lambda x: x+1, range(count))
end_time = time.time()        
filter_lambda_time = end_time - start_time
nice_print(str(filter_lambda_time))
#print len(list_a)
"""


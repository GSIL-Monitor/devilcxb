# -*- coding: utf-8 -*-


def bubbleSort(lists):
    """
    冒泡排序的思想: 每次比较两个相邻的元素, 如果他们的顺序错误就把他们交换位置
    如下：

    　　第一次：[1,4,0,5,6]

    　　第二次：[1,0,4,5,6]

    　　第三次：[0,1,4,5,6]

    　　第四次：[1,4,5,0,6]
    时间复杂度：O(n^2).  需要进行的比较次数为第一轮 n-1，n-2....1, 总的比较次数为 n*(n-1)/2
    """
    print lists
    for i in range(len(lists) - 1):  # 这个循环负责设置冒泡排序进行的次数
        for j in range(len(lists) - i - 1):  # 每一轮排完以后，最后一个数字都不需要再排列了，所以循环每次减一
            if lists[j] > lists[j + 1]:
                lists[j], lists[j + 1] = lists[j + 1], lists[j]
                print lists
    return lists


bubbleSort([7, 3, 1, 2, 4, 6, 5])

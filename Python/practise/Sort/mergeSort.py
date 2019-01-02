# -*- coding: utf-8 -*-


def merge(l_lists, r_lists):
    """
    这里显示了归并排序的第一步，将数组按照middle进行递归拆分，最后分到最细之后再将其使用对两个有序数组进行排序的方法对其进行排序。

两个有序数组排序的方法则非常简单，同时对两个数组的第一个位置进行比大小，将小的放入一个空数组，然后被放入空数组的那个位置的指针往后 移一个，然后继续和另外一个数组的上一个位置进行比较，以此类推。到最后任何一个数组先出栈完，就将另外i一个数组里的所有元素追加到新数组后面。

由于递归拆分的时间复杂度是logN 然而，进行两个有序数组排序的方法复杂度是N该算法的时间复杂度是N*logN 所以是NlogN。
    :param l_lists: 左边列表
    :param r_lists: 右边列表
    :return: 返回排列好的列表
    """
    temp_lists = []
    while True:
        if not l_lists or not r_lists:  # 其中一个列表被取空，则跳出循环
            break
        if l_lists[0] > r_lists[0]:
            temp_lists.append(r_lists[0])
            del r_lists[0]
        else:
            temp_lists.append(l_lists[0])
            del l_lists[0]
    if not l_lists:
        temp_lists += r_lists
    else:
        temp_lists += l_lists
    return temp_lists


def merge_sort(lists):
    if len(lists) == 1:  # 如果已经递归到最小单位，即可返回
        return lists
    middle = len(lists) / 2  # 拆分列表，直到取到最小单位
    l_lists = lists[:middle]
    r_lists = lists[middle:]
    left = merge_sort(l_lists)  # 递归取最小单位
    right = merge_sort(r_lists)  # 递归取最小单位
    return merge(left, right)  # 返回排列的结果


if __name__ == '__main__':
    a = [4, 7, 8, 3, 5, 9, 1, 2]
    print merge_sort(a)

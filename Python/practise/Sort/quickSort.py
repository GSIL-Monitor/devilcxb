# -*- coding: utf-8 -*-



def quick_sort(lists):
    """
    通过一趟排序将要排序的数据分割成独立的两部分，其中一部分的所有数据都比另外一部分的所有数据都要小，然后再按此方法对这两部分数据分别进行快速排序，整个排序过程可以递归进行，以此达到整个数据变成有序序列。
    :param lists: 穿入的列表
    :return: 返回排好的列表
    """
    count = len(lists)
    if count == 1:  # 如果长度为1，则直接返回
        return lists
    elif count == 2:  # 如果长度为2，则比较后返回
        if lists[0] > lists[1]:
            lists[0], lists[1] = lists[1], lists[0]
        return lists
    temp = lists[-1]  # 去最后一位数作为对比基数
    temp_lists = [temp]  # 并计入到临时表中
    bigger_count = 0
    for i in range(count - 1):  # 循环到倒数第二位，如果比基数大，则排到后面。
        if lists[i] > temp:
            lists.append(lists[i])
            del lists[i]
            bigger_count += 1
    final_list = temp_lists
    if bigger_count > 0:  # 如果存在比基数大的数，则递归基数大的数
        bigger_lists = lists[-bigger_count:]
        final_list = final_list + quick_sort(bigger_lists)
    if bigger_count != count - 1:  # 如果存在比基数小的数，则递归基数小的数
        smaller_lists = lists[:-bigger_count - 1]
        final_list = quick_sort(smaller_lists) + final_list
    return final_list


if __name__ == '__main__':
    print quick_sort([7, 3, 1, 2, 4, 8, 6, 5, 9])

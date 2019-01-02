# -*- coding: utf-8 -*-
import insertSort


def shell_insert_sort(lists, step):
    """
    希尔排序(Shell Sort)是插入排序的一种。也称缩小增量排序，是直接插入排序算法的一种更高效的改进版本。
    希尔排序是非稳定排序算法。该方法因DL．Shell于1959年提出而得名。 希尔排序是把记录按下标的一定增量分组，
    对每组使用直接插入排序算法排序；随着增量逐渐减少，每组包含的关键词越来越多，当增量减至1时，整个文件恰被分成一组，算法便终止。
    :param lists: 列表
    :param step: 步长
    :return: 排列好的数组
    """
    count = len(lists)
    group = count / step #定义需要划分几个子集
    while group > 1: #当划分的子集大于1时，循环
        lists = groups(lists, group)
        temp_lists = [None]*count # 创建空的临时集合
        for group_lists_index in range(len(lists)): #对每个子集的数字进行插入排序
            lists[group_lists_index][0] = insertSort.insert_sort(lists[group_lists_index][0])
        for group_lists in lists: #循环后得到一组新的数，用于下一轮循环
            for i in range(len(group_lists[0])):
                temp_lists[group_lists[1][i]] = group_lists[0][i]
        lists = temp_lists
        print lists
        step += 1
        group = count / step
    return lists


def groups(lists, group):
    """
    根据希尔排序要求，创建分组,每一个子分组包含数值和下标两个集合，如[[[7, 2, 5], [0, 4, 8]], [[3, 9], [1, 5]], [[8, 4], [2, 6]], [[1, 6], [3, 7]]]
    :param lists: 列表
    :param group: 分组个数
    :return: 分组好的二维数组
    """
    new_lists = []
    for i in range(group):
        temp_list = [[lists[i]], [i]]
        j = i + group
        while j < len(lists):
            temp_list[0].append(lists[j]) # 自分组添加数值
            temp_list[1].append(j)# 子分组添加下标
            j += group
        new_lists.append(temp_list)
    return new_lists


if __name__ == '__main__':
    print shell_insert_sort([7, 3, 8, 1, 2, 9, 4, 6, 5], 2)

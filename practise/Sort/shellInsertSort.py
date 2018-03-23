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
    print lists
    count = len(lists)
    group = count / step
    print group
    while group > 1:
        lists = groups(lists, group)
        print lists
        lists = reduce(lambda x, y: x + y, map(lambda x: insertSort.insert_sort(x), lists))
        print lists
        step += 1
        group = count / step
    return insertSort.insert_sort(lists)


def groups(lists, group):
    """
    根据希尔排序要求，创建分组
    :param lists: 列表
    :param group: 分组个数
    :return: 分组好的二维数组
    """
    new_lists = []
    for i in range(group):
        temp_list = [lists[i]]
        j = i + group
        while j < len(lists):
            temp_list.append(lists[j])
            j += group
        new_lists.append(temp_list)
    return new_lists


if __name__ == '__main__':
    shell_insert_sort([7, 3, 1, 2, 4, 6, 5], 2)

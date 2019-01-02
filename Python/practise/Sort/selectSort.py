# -*- coding: utf-8 -*-


def select_insert(lists):
    """
    从第二位开始循环，与第一位数字进行比较，找出最小的放到第一位；然后从第三位开始，找出最小的放到第二位，以此类推。
    :param lists: 列表
    :return: 选择排序好的列表
    """
    for i in range(len(lists)):  # 循环所有数字
        for j in range(i + 1, len(lists)):  # 循环当前数字后面的数字，如果比当前的数字小，就替换当前的数字，直到完成
            if lists[i] > lists[j]:
                lists[j], lists[i] = lists[i], lists[j]
    return lists


if __name__ == '__main__':
    print select_insert([7, 3, 1, 2, 4, 6, 5])

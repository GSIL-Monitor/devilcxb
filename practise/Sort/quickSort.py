# -*- coding: utf-8 -*-


def quick_sort(lists):
    """
    1.选取一个数字作为基准，可选取末位数字
    2.将数列第一位开始，依次与此数字比较，如果小于此数，将小数交换到左边，最后达到小于基准数的在左边，大于基准数的在右边，分为两个数组
    3.分别对两个数组重复上述步骤
    :param lists: 传入的list
    :return: 排序结果
    """
    count = len(lists)
    if count == 1:  # 如果数量为1，直接返回
        return lists
    if count == 2:  # 如果数量为2，直接对比返回
        if lists[0] > lists[1]:
            lists[0], lists[1] = lists[1], lists[0]
        return lists
    temp = lists[-1]  # 取最后一位做对比的基数
    large_count = 0
    temp_lists = [temp]  # 并放入到临时的列表里面
    for i in range(count - 2):  # 按照快速排序的理念，比基数大的放在后面。
        if lists[i] > temp:
            lists.append(lists[i])
            del lists[i]
            large_count += 1
    final_lists = temp_lists
    if large_count > 0:  # 如果存在比基数大的数字，则递归
        larger_lists = lists[-large_count:]
        larger_sorted_lists = quick_sort(larger_lists)
        final_lists = final_lists + larger_sorted_lists  # 拼接大的数在基数的后面
    if large_count != count:  # 如果存在比基数小的数字，则递归
        smaller_lists = lists[:-large_count - 1]
        smaller_sorted_lists = quick_sort(smaller_lists)
        final_lists = smaller_sorted_lists + final_lists  # 拼接小的数在前面
    print "final lists is {}".format(final_lists)
    return final_lists


if __name__ == '__main__':
    quick_sort([7, 3, 1, 2, 4, 6, 5])

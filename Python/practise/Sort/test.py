def shift(lists, shift_num):
    """

    :param lists:
    :param shift_num:
    :return:
    """
    lists = map(lambda x: x[1], sorted(map(lambda x: ((x + shift_num)%len(lists), lists[x]), range(len(lists)))))
    return lists

if __name__ == '__main__':
    print shift(range(5), 2)

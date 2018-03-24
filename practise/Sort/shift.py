# -*- coding: utf-8 -*-
def shift(lists, shift_num):
    """

    :param lists:
    :param shift_num:
    :return:
    """
    return map(lambda x: x[1], sorted(map(lambda x: ((x + shift_num) % len(lists), lists[x]), range(len(lists)))))


if __name__ == '__main__':
    print shift(range(5), 2)

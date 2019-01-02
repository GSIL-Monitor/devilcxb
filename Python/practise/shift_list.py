def shift(lists, shift_num):
    temp_lists = ["", "", "", "", ""]
    for i in range(len(lists)):
        value = lists[i]
        if i + shift_num >= len(lists):
            i = (i + shift_num)%len(lists)
        else:
            i = i + shift_num
        print i, value
        temp_lists[i] = value
    return temp_lists

if __name__ == '__main__':
    print shift(["a", "b", "c", "d", "e"], 10)
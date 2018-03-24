def shift(lists, shift_num):
    temp_lists = [None]*len(lists)
    lists = ["a", "b", "c", "d", "e"]
    lists = map(lambda x: (lists[x], (x + shift_num)%len(lists)), range(len(lists)))
    for i in lists:
        temp_lists[i[1]] = i[0]
    return temp_lists

if __name__ == '__main__':
    print shift(["a", "b", "c", "d", "e"], -5)
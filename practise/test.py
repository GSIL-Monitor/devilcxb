def groups(lists, group):
    new_lists = []
    for i in range(group):
        temp_list = [lists[i]]
        j = i + group
        while j < len(lists):
            temp_list.append(lists[j])
            j += group
        new_lists.append(temp_list)
    return new_lists

print groups([7, 3, 1, 2, 4, 6, 5], 3)
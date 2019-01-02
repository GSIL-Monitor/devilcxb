a = [1, 2, 4, 4]
b = [5, 3, 6, 6, 2]
print set(a)
print set(b)
print set(a).isdisjoint(set(b))
print set(b).isdisjoint(set(a))
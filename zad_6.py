def pot(l1: list, l2: list) -> list:
    k = l1 + l2
    k = list(set(k))
    k = [i ** 3 for i in k]
    return k

print(pot([2,3],[3,4]))
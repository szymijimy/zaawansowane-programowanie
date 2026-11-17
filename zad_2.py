def imiona(items):
    print(items)
    return


print("Podpunkt: A")
imion = ["Basia", "Kasia", "Asia", "Tosia", "Zosia"]
imiona(imion)


def liczba(items):
    for i in range(len(items)):
        items[i] = items[i] * 2
    return items


def liczba2(items):
    items = [x * 2 for x in items]
    return items


print("Podpunkt: B")
values = [22, 33, 44, 55, 66]
print(liczba(values))
values = [22, 33, 44, 55, 66]
print(liczba2(values))


def parzyste(items):
    g = []
    for i in range(len(items)):
        if items[i] % 2 == 0:
            g.append(items[i])
    return g


print("Podpunkt: C")
values = [22, 33, 44, 55, 66] * 2
print(parzyste(values))


def drugi(items):
    g = []
    for i in range(0, len(items), 2):
        g.append(items[i])
    return g


print("Podpunkt: D")
values = [22, 33, 44, 55, 66] * 2
print(drugi(values))

def imiona(l):
    print(l)
    return

print("Podpunkt: A")
imion = ["Basia", "Kasia", "Asia", "Tosia", "Zosia"]
imiona(imion)

def liczba(l):
    for i in range(len(l)):
        l[i] = l[i]*2
    return l
def liczba2(l):
    l = [x * 2 for x in l]
    return l

print("Podpunkt: B")
l = [22, 33, 44, 55, 66]
print(liczba(l))
l = [22, 33, 44, 55, 66]
print(liczba2(l))

def parzyste(l):
    g = []
    for i in range(len(l)):
        if l[i] % 2 == 0:
            g.append(l[i])
    return g

print("Podpunkt: C")
l = [22, 33, 44, 55, 66] * 2
print(parzyste(l))

def drugi(l):
    g = []
    for i in range(0, len(l), 2):
        g.append(l[i])
    return g

print("Podpunkt: D")
l = [22, 33, 44, 55, 66] * 2
print(drugi(l))

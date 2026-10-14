def czy(x) -> bool:
    if x % 2 == 0:
        return True
    else:
        return False

if czy(3) == True:
    print("Liczba parzysta")
else:
    print("Liczba nieparzysta")

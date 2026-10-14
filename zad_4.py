def czy(x: int, y: int, z: int) -> bool:
    if x + y >= z:
        return True
    else:
        return False

if czy(2,1,5) == True:
    print("Wienkże")
else:
    print("Mińsze")
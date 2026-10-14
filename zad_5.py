def czy(l: list, x: int) -> bool:
    if x in l:
        return True
    else:
        return False

print(czy([2,3,5], 4))
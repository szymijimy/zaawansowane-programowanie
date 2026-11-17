def czy(items: list, x: int) -> bool:
    if x in items:
        return True
    else:
        return False


print(czy([2, 3, 5], 4))

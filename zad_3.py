class Property():
    def __init__(self, area, rooms: int, price, address):
        self.area = area
        self.rooms = rooms
        self.price = price
        self.address = address

class House(Property):
    def __init__(self, area, rooms: int, price, address, plot: int):
        super().__init__(area, rooms, price, address)
        self.plot = plot

    def __str__(self):
        return f'{self.area}, {self.rooms}, {self.price}, {self.address}, {self.plot}'

class Flat(Property):
    def __init__(self, area, rooms, price, address, floor: int):
        super().__init__(area, rooms, price, address)
        self.floor = floor

    def __str__(self):
        return f'{self.area}, {self.rooms}, {self.price}, {self.address}, {self.floor}'

house1 = House(150, 5, 750000, "Słoneczna 12, Tychy", 500)
flat1 = Flat(65, 3, 450000, "Kwiatowa 5/2, Piasek", 2)

print(house1)
print(flat1)
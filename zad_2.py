class Library():
    def __init__(self, city, street, zip_code, open_hours: str, phone):
        self.city = city
        self.street = street
        self.zip_code = zip_code
        self.open_hours = open_hours
        self.phone = phone

    def __str__(self):
        return f'{self.city}, {self.street}, {self.zip_code}, {self.open_hours}, {self.phone}'

class Employee():
    def __init__(self, first_name, last_name, hire_date, birth_date, 
                 city, street, zip_code, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.hire_date = hire_date
        self.birth_date = birth_date
        self.city = city
        self.street = street
        self.zip_code = zip_code
        self.phone = phone

    def __str__(self):
        return f'{self.first_name}, {self.last_name}, {self.hire_date}, {self.birth_date}, {self.city}, {self.street},  {self.zip_code}, {self.phone}'

class Book():
    def __init__(self, library: Library, publication_date, author_name, 
                 author_surname, number_of_pages: int):
        self.library = library
        self.publication_date = publication_date
        self.author_name = author_name
        self.author_surname = author_surname
        self.number_of_pages = number_of_pages

    def __str__(self):
        return f'{self.library}, {self.publication_date}, {self.author_name}, {self.author_surname}, {self.number_of_pages}'

class Order():
    def __init__(self, employee: Employee, student: Student, books: list[Book], order_date):
        self.employee = employee
        self.student = student
        self.books = books
        self.order_date = order_date

    def __str__(self):
        book_str = ", ".join(str(book) for book in self.books)
        return f'{self.employee}, {self.student}, [{book_str}], {self.order_date}'

class Student():
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

bibl1 = Library("Tychy", "Frycza Modrzewskiego 21", "43-100", "7:30-17:30", "000-111-222")
bibl2 = Library("Piasek", "Katowicka 10", "43-211", "8:00-16:00", "333-444-555")

book1 = Book(bibl1, "15-12-2024", "Jonasz", "Jonaski", 340)
book2 = Book(bibl1, "15-12-2016", "Jonasz", "Jonaskowski", 341)
book3 = Book(bibl1, "15-12-2023", "Jonasz", "Jonasecki", 342)
book4 = Book(bibl2, "05-10-2020", "Jonasz", "Jonas", 343)
book5 = Book(bibl2, "15-12-2021", "Jonasz", "Jonasowy", 344)

employee1 = Employee("Izaak", "Izaakowski", "12-01-2020", "08-08-2000", "Belgrad", "Milunki Savić", "87-200", "123-123-123")
employee2 = Employee("Izaak", "Izaakinki", "10-12-2018", "12-02-1999", "Sarajewo", "Biljany Plavsić", "85-200", "223-223-223")
employee3 = Employee("Izaak", "Izaaaa", "11-03-2017", "24-02-1992", "Zagrzeb", "Mariji Jurić Zgorka", "86-200", "323-323-323")

stud1 = Student("Zygfryd", "Steinberg")
stud2 = Student("Hildegarda", "von Bock")
stud3 = Student("Baltazar", "Bożydarowski")

order1 = Order(employee1, stud1, [book1, book2], "03-03-2026")
order2 = Order(employee3, stud3, [book3, book4, book5], "04-03-2026")

print(order1)
print(order2)

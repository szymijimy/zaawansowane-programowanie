class Student():
    def __init__(self, name: str, marks: list):
        self.name = name
        self.marks = marks

    def is_passed(self) -> bool:
        a = (sum(self.marks) / len(self.marks) / 5) * 100
        
        return a > 50
        
student1 = Student("Jonasz", [4, 4, 4])
student2 = Student("Izaak", [2, 3, 1])

print(student1.is_passed())
print(student2.is_passed())

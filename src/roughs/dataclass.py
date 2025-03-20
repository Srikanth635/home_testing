from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List


class Mine:
    ...

class Mine2:
    pass

class Mix1:
    def method1(self):
        print("Im Mix1 class method1")

class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abstractmethod
    def prints(self):
        print("Im Shape.prints")

class Circle(Shape):
    def __init__(self, radius):
        print("Im Circle init.")
        super().__init__(x=1,y=1)
        self.radius = radius

    def prints(self):
        print(f"Circle {self.x, self.y, self.radius}")

class Rectangle(Shape):
    def __init__(self, width, height):
        print("Im Rectangle init.")
        self.width = width
        self.height = height
        super().__init__(x=1,y=1)
        self.width = width
        self.height = height

    def method1(self):
        print(f"Rectangle Mix {self.x, self.y, self.width, self.height}")

    def prints(self):
        print(f"Rectangle {self.x, self.y, self.width, self.height}")


class Singleton:
    def __init__(self,first_name,last_name):
        self.first_name = first_name
        self.last_name = last_name
        print("Im Singleton")

    _instance = None

    def __getattr__(self, item):
        print("Overloading getattr")
        attr = getattr(self, item)
        return f"attribute is {attr}"

    def __new__(cls, *args, **kwargs):

        print(f'variable arguments passed: {args}')
        print(f'variable keyword arguments passed: {kwargs}, type {type(kwargs)}')

        if not hasattr(cls, "_instance") or cls._instance is None:
            print("Creating new instance")
            cls._instance = super().__new__(cls)
        else:
            print(f"Instance already exists")

        return cls._instance

def teams() -> List[str]:
    return ['srh', 'rcb', 'csk', 'mi', 'kkr']

@dataclass(frozen=True)
class IPL:
    no_of_teams : int = field(default=10)
    teams: list[str] = field(init=False, default_factory=teams)


class Robot(Circle, Rectangle):
    def __init__(self, radius, width, height):
        super().__init__(radius)
        self.width = width
        self.height = height

    def prints(self):
        print("Robot prints")

class Base:
    def __init__(self):
        print("Base init")
        self.value = 10

class Left(Base):
    def __init__(self):
        print("Left init")
        Base.__init__(self)
        self.value += 5

class Right(Base):
    def __init__(self):
        print("Right init")
        Base.__init__(self)
        self.value *= 2

class Bottom(Left, Right):
    def __init__(self):
        print("Bottom init")
        Left.__init__(self)
        Right.__init__(self)

if __name__ == '__main__':

    bt = Bottom()
    print(bt.value)

    sing = Singleton(last_name="malineni", first_name="srikanth")

    # print(sing.__getattr__("last_name"))

    ipl = IPL()

    # ipl.teams = ipl.teams + ['dc']

    print(repr(ipl))

    cir = Circle(2)
    print(Circle.__mro__)
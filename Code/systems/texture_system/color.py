from typing import Tuple


class Color:
    __slots__ = ['_r', '_g', '_b', '_a']
    
    def __init__(self, r: int, g: int, b: int, a: int) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @property
    def r(self) -> int:
        return self._r
    
    @r.setter
    def r(self, value: int) -> None:
        if not (0 <= value <= 255):
            raise ValueError("Invalid value for r. It must be between 0 and 255")
        
        self._r = value
    
    @property
    def g(self) -> int:
        return self._g
    
    @g.setter
    def g(self, value: int) -> None:
        if not (0 <= value <= 255):
            raise ValueError("Invalid value for g. It must be between 0 and 255")
        
        self._g = value
    
    @property
    def b(self) -> int:
        return self._b
    
    @b.setter
    def b(self, value: int) -> None:
        if not (0 <= value <= 255):
            raise ValueError("Invalid value for b. It must be between 0 and 255")
        
        self._b = value
    
    @property
    def a(self) -> int:
        return self._a
    
    @a.setter
    def a(self, value: int) -> None:
        if not (0 <= value <= 255):
            raise ValueError("Invalid value for a. It must be between 0 and 255")
        
        self._a = value
    
    def __str__(self) -> str:
        return f"{self.r}_{self.g}_{self.b}_{self.a}"

    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    @staticmethod
    def from_tuple(value: Tuple[int, int, int, int]) -> "Color":
        return Color(value[0], value[1], value[2], value[3])
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.r, self.g, self.r, self.a)

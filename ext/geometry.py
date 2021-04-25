

class Coord:
    x: int
    y: int

    def __init__(self, *, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Coord(x={self.x}, y={self.y})'

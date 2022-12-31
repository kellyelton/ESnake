import random
from typing import Optional


class Direction:
    def __init__(self, direction: Optional[str] = None):
        if direction is None:
            self.string = "none"
            self.num = -1
            return

        if isinstance(direction, str):
            direction = direction.casefold()

            if direction == "left".casefold(): 
                self.string = "left"
                self.num = 0
            elif direction == "right".casefold():
                self.string = "right"
                self.num = 1 
            elif direction == "up".casefold():
                self.string = "up"
                self.num = 2
            elif direction == "down".casefold():
                self.string = "down"
                self.num = 3
            elif direction == "none".casefold():
                self.string = "none"
                self.num = -1
            else: raise Exception("Invalid direction: " + str(direction))
        else: raise Exception("Invalid direction: " + str(direction))


    @staticmethod
    def left() -> "Direction":
        return DIRECTION_LEFT
    
    @staticmethod
    def right() -> "Direction":
        return DIRECTION_RIGHT
    
    @staticmethod
    def up() -> "Direction":
        return DIRECTION_UP
    
    @staticmethod
    def down() -> "Direction":
        return DIRECTION_DOWN
    
    @staticmethod
    def none() -> "Direction":
        return DIRECTION_NONE

    @property
    def opposite(self):
        if self.num == DIRECTION_LEFT.num:
            return DIRECTION_RIGHT
        elif self.num == DIRECTION_RIGHT.num:
            return DIRECTION_LEFT
        elif self.num == DIRECTION_UP.num:
            return DIRECTION_DOWN
        elif self.num == DIRECTION_DOWN.num:
            return DIRECTION_UP
        elif self.num == DIRECTION_NONE.num:
            return DIRECTION_NONE
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeRight(self):
        if self.num == DIRECTION_LEFT.num:
            return DIRECTION_UP
        elif self.num == DIRECTION_RIGHT.num:
            return DIRECTION_DOWN
        elif self.num == DIRECTION_UP.num:
            return DIRECTION_RIGHT
        elif self.num == DIRECTION_DOWN.num:
            return DIRECTION_LEFT
        elif self.num == DIRECTION_NONE.num:
            return DIRECTION_NONE
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeLeft(self):
        if self.num == DIRECTION_LEFT.num:
            return DIRECTION_DOWN
        elif self.num == DIRECTION_RIGHT.num:
            return DIRECTION_UP
        elif self.num == DIRECTION_UP.num:
            return DIRECTION_LEFT
        elif self.num == DIRECTION_DOWN.num:
            return DIRECTION_RIGHT
        elif self.num == DIRECTION_NONE.num:
            return DIRECTION_NONE
        else: raise Exception(f"Invalid direction: {self.string}")

    def toVector(self):
        if self.num == DIRECTION_NONE.num:
            return (0, 0)

        x = 0
        if self.num == DIRECTION_LEFT.num: # left
            x = -1
        elif self.num == DIRECTION_RIGHT.num: #right
            x = 1

        y = 0
        if self.num == DIRECTION_UP.num: # Up
            y = -1
        elif self.num == DIRECTION_DOWN.num: # down
            y = 1

        return (x, y)

    @staticmethod
    def random():
        return random.choice([DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_DOWN])

    def __str__(self):
        self.string
        
    def __eq__(self, value):
        if value == None:
            return False
        elif isinstance(value, Direction):
            return value.num == self.num
        elif isinstance(value, str):
            return value.casefold() == self.str.casefold()
        else:
            return False

DIRECTION_LEFT = Direction("left")
DIRECTION_RIGHT = Direction("right")
DIRECTION_UP = Direction("up")
DIRECTION_DOWN = Direction("down")
DIRECTION_NONE = Direction("none")
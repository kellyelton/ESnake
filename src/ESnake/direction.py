class Direction:
    @property
    def opposite(self):
        if self.num == Direction.left.num:
            return Direction.right
        elif self.num == Direction.right.num:
            return Direction.left
        elif self.num == Direction.up.num:
            return Direction.down
        elif self.num == Direction.down.num:
            return Direction.up
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeRight(self):
        if self.num == Direction.left.num:
            return Direction.up
        elif self.num == Direction.right.num:
            return Direction.down
        elif self.num == Direction.up.num:
            return Direction.right
        elif self.num == Direction.down.num:
            return Direction.left
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeLeft(self):
        if self.num == Direction.left.num:
            return Direction.down
        elif self.num == Direction.right.num:
            return Direction.up
        elif self.num == Direction.up.num:
            return Direction.left
        elif self.num == Direction.down.num:
            return Direction.right
        else: raise Exception(f"Invalid direction: {self.string}")

    def toVector(self):
        x = 0
        if self.num == Direction.left.num: # left
            x = -1
        elif self.num == Direction.right.num: #right
            x = 1

        y = 0
        if self.num == Direction.up.num: # Up
            y = -1
        elif self.num == Direction.down.num: # down
            y = 1

        return (x, y)

    def __init__(self, direction):
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
            else: raise Exception("Invalid direction: " + str(direction))
        else: raise Exception("Invalid direction: " + str(direction))

    def __str__(self):
        self.string
        
    def __eq__(self, value):
        if value == None:
            return False
        elif isinstance(value, Direction):
            return value.num == self.num
        elif isinstance(value, str):
            return value.casefold() == self.value.casefold()
        else:
            return False

Direction.left = Direction("left")
Direction.right = Direction("right")
Direction.up = Direction("up")
Direction.down = Direction("down")
class Direction:
    @property
    def opposite(self):
        if self.string == "left":
            return Direction.right
        elif self.string == "right":
            return Direction.left
        elif self.string == "up":
            return Direction.down
        elif self.string == "down":
            return Direction.up
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeRight(self):
        if self.string == "left":
            return Direction.up
        elif self.string == "right":
            return Direction.down
        elif self.string == "up":
            return Direction.right
        elif self.string == "down":
            return Direction.left
        else: raise Exception(f"Invalid direction: {self.string}")

    @property
    def relativeLeft(self):
        if self.string == "left":
            return Direction.down
        elif self.string == "right":
            return Direction.up
        elif self.string == "up":
            return Direction.left
        elif self.string == "down":
            return Direction.right
        else: raise Exception(f"Invalid direction: {self.string}")

    def toVector(self):
        x = 0
        if self.string == "left":
            x = -1
        elif self.string == "right":
            x = 1

        y = 0
        if self.string == "up":
            y = -1
        elif self.string == "down":
            y = 1

        return (x, y)

    def __init__(self, direction):
        if isinstance(direction, str):
            direction = direction.casefold()

            if direction == "left".casefold(): 
                self.string = "left"
            elif direction == "right".casefold():
                self.string = "right"
            elif direction == "up".casefold():
                self.string = "up"
            elif direction == "down".casefold():
                self.string = "down"
            else: raise Exception("Invalid direction: " + str(direction))
        else: raise Exception("Invalid direction: " + str(direction))

    def __str__(self):
        self.string
        
    def __eq__(self, value):
        if value == None:
            return False
        elif isinstance(value, Direction):
            return value.string == self.string
        elif isinstance(value, str):
            return value.casefold() == self.value.casefold()
        else:
            return False

Direction.left = Direction("left")
Direction.right = Direction("right")
Direction.up = Direction("up")
Direction.down = Direction("down")
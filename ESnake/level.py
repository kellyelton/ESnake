class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.score = 0
        self.playerDirection = None
        self.playerLocation = self.center
        self.foodLocation = self.randomLocation
    
    @property
    def center(self):
        return (self.width / 2, self.height / 2)
    
    @property
    def randomLocation(self):
        #TODO actually randomize
        return (12, 12)
    
    def update(self, app):
        newPlayerLocation = self.playerLocation

        if self.playerDirection == None:
            return
        elif self.playerDirection == "left":
            newPlayerLocation = (self.playerLocation[0] - 1, self.playerLocation[1])
        elif self.playerDirection == "right":
            newPlayerLocation = (self.playerLocation[0] + 1, self.playerLocation[1])
        elif self.playerDirection == "up":
            newPlayerLocation = (self.playerLocation[0], self.playerLocation[1] - 1)
        elif self.playerDirection == "down":
            newPlayerLocation = (self.playerLocation[0], self.playerLocation[1] + 1)

        self.playerLocation = newPlayerLocation
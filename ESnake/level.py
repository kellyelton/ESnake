import random
from random import randint
from .appscreen import AppScreen

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.score = 0
        self.playerDirection = None
        self.playerLocations = [self.center]
        self.playerSpeed = 10 # Tiles per second
        self.playerLastTimeMoved = 0
        self.foodLocation = self.randomLocation
    
    @property
    def center(self):
        return (self.width / 2, self.height / 2)

    @property
    def randomLocation(self):
        x = randint(0, self.width)
        y = randint(0, self.height)

        return (x, y)
    
    @property
    def randomEmptyLocation(self):
        location = self.randomLocation

        while not self.isEmpty(location):
            location = self.randomLocation

        return location
    
    def update(self, app, time):
        minDelay = 1000 / self.playerSpeed

        msSincePlayerLastMoved = time - self.playerLastTimeMoved

        if msSincePlayerLastMoved >= minDelay:
            self.playerLastTimeMoved = time
            self.movePlayer(app)

    def movePlayer(self, app):
        newPlayerLocation = self.playerLocation

        newLocationContents = self.getContents(newPlayerLocation)

        if newLocationContents == "food":
            self.score += 1
            self.foodLocation = self.randomEmptyLocation
        elif newLocationContents == "player":
            app.screen = AppScreen.PostGame
            return
        elif newLocationContents == "wall":
            app.screen = AppScreen.PostGame 
            return

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
     
    def getContents(self, location):
        if location == self.playerLocation:
            return "player"
        elif location == self.foodLocation:
            return "food"
        
        if location[0] < 0: return "wall"
        if location[0] > self.width: return "wall"

        if location[1] < 0: return "wall"
        if location[1] > self.height: return "wall"

        return None

    def isEmpty(self, location):
        if location == self.playerLocation:
            return False
        elif location == self.foodLocation:
            return False
        else:
            return True
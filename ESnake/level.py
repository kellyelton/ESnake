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
        self.playerSpeed = 15 # Tiles per second
        self.playerLastTimeMoved = 0
        self.playerDeathTime = 0
        self.isPlayerDead = False
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
        if not self.isPlayerDead:
            minDelay = 1000 / self.playerSpeed

            msSincePlayerLastMoved = time - self.playerLastTimeMoved

            if msSincePlayerLastMoved >= minDelay:
                self.playerLastTimeMoved = time
                self.movePlayer(app, time)
        else:
            msSincePlayerDied = time - self.playerDeathTime

            if msSincePlayerDied >= 3000:
                app.screen = AppScreen.PostGame

    def movePlayer(self, app, time):
        if self.playerDirection == None: return

        oldLocation = self.playerLocations[0]
        newLocation = oldLocation
        removeTail = True

        if self.playerDirection == "left":
            newLocation = (oldLocation[0] - 1, oldLocation[1])
        elif self.playerDirection == "right":
            newLocation = (oldLocation[0] + 1, oldLocation[1])
        elif self.playerDirection == "up":
            newLocation = (oldLocation[0], oldLocation[1] - 1)
        elif self.playerDirection == "down":
            newLocation = (oldLocation[0], oldLocation[1] + 1)

        newLocationContents = self.getContents(newLocation)

        if newLocationContents == "food":
            self.score += 1
            self.foodLocation = self.randomEmptyLocation
            removeTail = False
        elif newLocationContents == "player":
            self.isPlayerDead = True
            self.playerDeathTime = time
        elif newLocationContents == "wall":
            self.isPlayerDead = True
            self.playerDeathTime = time

        self.playerLocations.insert(0, newLocation)

        if removeTail:
            self.playerLocations.pop()
     
    def getContents(self, location):
        if location == self.foodLocation:
            return "food"
        
        for playerLocation in self.playerLocations:
            if location == playerLocation:
                return "player"
        
        if location[0] < 0: return "wall"
        if location[0] > self.width: return "wall"

        if location[1] < 0: return "wall"
        if location[1] > self.height: return "wall"

        return None

    def isEmpty(self, location):
        if location == self.foodLocation:
            return False

        for playerLocation in self.playerLocations:
            if location == playerLocation:
                return False

        return True
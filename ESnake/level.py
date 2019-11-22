import random
from random import randint
from .appscreen import AppScreen
from .direction import Direction

class Level:
    @staticmethod
    def default():
        return Level(15, 15, 5)

    def __init__(self, width, height, speed):
        self.width = width
        self.height = height
        self.playerSpeed = speed #tiles per second

        #TODO: abstract the player into its own class
        self.score = 0
        self.playerDirection: Direction = None
        self.requestedPlayerDirection: Direction = None
        self.playerLocations = [self.center]
        self.playerLastTimeMoved = 0
        self.playerDeathTime = 0
        self.isPlayerDead = False
        self.foodLocation = None # Needs to exist before we set it to random
        self.foodLocation = self.randomEmptyLocation
    
    @property
    def center(self):
        return (self.width // 2, self.height // 2)

    @property
    def randomLocation(self):
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)

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
        newDirection = self.requestedPlayerDirection
        self.requestedPlayerDirection = None

        if newDirection != None and self.playerDirection != newDirection:
            # Don't allow reversing if we have a tail
            if len(self.playerLocations) > 1:
                if self.playerDirection.opposite == newDirection:
                    newDirection = self.playerDirection # cancel out change

            self.playerDirection = newDirection

        if self.playerDirection == None: return

        oldLocation = self.playerLocations[0]
        newLocation = oldLocation
        removeTail = True

        if self.playerDirection == Direction.left:
            newLocation = (oldLocation[0] - 1, oldLocation[1])
        elif self.playerDirection == Direction.right:
            newLocation = (oldLocation[0] + 1, oldLocation[1])
        elif self.playerDirection == Direction.up:
            newLocation = (oldLocation[0], oldLocation[1] - 1)
        elif self.playerDirection == Direction.down:
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
        
        if location[0] <= 0: return "wall"
        if location[0] >= self.width - 1: return "wall"

        if location[1] <= 0: return "wall"
        if location[1] >= self.height - 1: return "wall"

        return None

    def isEmpty(self, location):
        if location == self.foodLocation:
            return False

        for playerLocation in self.playerLocations:
            if location == playerLocation:
                return False

        if location[0] <= 0 or location[0] >= self.width - 1:
            return False
        if location[1] <= 0 or location[1] >= self.height - 1:
            return False 

        return True
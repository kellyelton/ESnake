import random
import logging
from random import randint
from . import updateHighScore, AppScreen, Snake

class Level:
    @staticmethod
    def default():
        return Level(40, 40, 8)

    def __init__(self, width, height, speed):
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.foodLocation = None # Needs to exist before we set it to random
        self.player = Snake(speed, self.center)
        self.bots = [Snake(speed, self.randomEmptyLocation)]

        self.foodLocation = self.randomEmptyLocation
        self.startTime: int = None
    
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
        self.player.update(app, time, self)

        if self.player.isDead:
            msSincePlayerDied = time - self.player.deathTime

            if msSincePlayerDied >= 3000:
                self.logger.debug("done with death delay")
                app.screen = AppScreen.PostGame
                storedHighScore = updateHighScore(app.config, self.player.score)
                if storedHighScore:
                    self.logger.debug("Got a high score")

    def getContents(self, location):
        if hasattr(self, "foodLocation"):
            if location == self.foodLocation:
                return "food"

        if hasattr(self, "player"):
            for segment in self.player.segments:
                if location == segment:
                    return "player"

        if hasattr(self, "bots"):
            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment:
                        return "bot"
        
        if location[0] <= 0: return "wall"
        if location[0] >= self.width - 1: return "wall"

        if location[1] <= 0: return "wall"
        if location[1] >= self.height - 1: return "wall"

        return None

    def isEmpty(self, location):
        if hasattr(self, "foodLocation"):
            if location == self.foodLocation:
                return False

        if hasattr(self, "player"):
            for segment in self.player.segments:
                if location == segment:
                    return False

        if hasattr(self, "bots"):
            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment:
                        return False

        if location[0] <= 0 or location[0] >= self.width - 1:
            return False
        if location[1] <= 0 or location[1] >= self.height - 1:
            return False 

        return True

    def moveFood(self):
        self.foodLocation = self.randomEmptyLocation

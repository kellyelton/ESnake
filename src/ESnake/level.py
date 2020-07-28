import random
import logging
from random import randint
from . import updateHighScore, AppScreen, Snake, Food, Wall
from .controllers import Dylan

class Level:
    @staticmethod
    def default():
        return Level(40, 40, 8)

    def __init__(self, width, height, speed):
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.foods = [Food(self.randomEmptyLocation)]
        self.player = Snake(speed, self.center, ["player"])
        self.bots = [
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan())
        ]

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

        for bot in self.bots:
            bot.update(app, time, self)
            if bot.isDead:
                msSincePlayerDied = time - bot.deathTime

                if msSincePlayerDied >= 3000:
                    self.logger.debug("done with death delay")
                    self.bots.append(Snake(bot.speed, self.randomEmptyLocation, ["bot"], Dylan()))
                    self.bots.remove(bot)

    def getContents(self, location):
        if hasattr(self, "foods"):
            for food in self.foods:
                if location == food.location:
                    return food

        if hasattr(self, "player"):
            for segment in self.player.segments:
                if location == segment:
                    return self.player

        if hasattr(self, "bots"):
            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment:
                        return bot
        
        if location[0] <= 0: return Wall(location)
        if location[0] >= self.width - 1: return Wall(location)

        if location[1] <= 0: return Wall(location)
        if location[1] >= self.height - 1: return Wall(location)

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

    def moveFood(self, food):
        food.location = self.randomEmptyLocation

import random
import logging
import numpy as np
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
        self.foods = []
        self.player = None
        self.bots = []
        self.occupiedLocations = None
        self.timeOffset = 0
        self.lastUpdateTime = 0
        self.foods = [
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
            Food(self.randomEmptyLocation),
        ]
        self.player = Snake(speed, self.center, ["player"])
        self.bestBot = None
        self.bots = [
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
            Snake(speed, self.randomEmptyLocation, ["bot"], Dylan()),
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
        time = time + self.timeOffset

        self.lastUpdateTime = time

        self.player.update(app, time, self)

        self.refreshOccupiedLocations()
        
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

            self.refreshOccupiedLocations()

            if bot.isDead:
                msSincePlayerDied = time - bot.deathTime

                if msSincePlayerDied >= 1000:
                    self.logger.debug("done with death delay")

                    if self.bestBot == None or bot.score > self.bestBot.score:
                        bestScore = "none"
                        if self.bestBot != None:
                            bestScore = self.bestBot.score
                        self.logger.info(f"Bot got new high score {bot.score} > {bestScore}")
                        self.bestBot = bot

                    newController = Dylan(self.bestBot.controller)
                    newBot = Snake(bot.speed, self.randomEmptyLocation, ["bot"], newController)

                    self.bots.append(newBot)
                    self.bots.remove(bot)

                    self.refreshOccupiedLocations()

    def refreshOccupiedLocations(self):
        if self.occupiedLocations is None:
            self.occupiedLocations = np.empty(shape=(self.height,self.width),dtype='object')
        else:
            self.occupiedLocations.fill(None)

        for food in self.foods:
            self.occupiedLocations[food.location[0]][food.location[1]] = food

        if self.player != None:
            for segment in self.player.segments:
                self.occupiedLocations[segment[0]][segment[1]] = self.player

        for bot in self.bots:
            for segment in bot.segments:
                self.occupiedLocations[segment[0]][segment[1]] = bot

        for x in range(self.width):
            self.occupiedLocations[0][x] = Wall((x, 0))
            self.occupiedLocations[self.height - 1][x] = Wall((x, self.height - 1))

        for y in range(self.height):
            self.occupiedLocations[y][0] = Wall((0, y))
            self.occupiedLocations[y][self.width - 1] = Wall((self.width - 1, y))

    def getContents(self, location):
        if self.isOutsideWall(location): return None

        if self.occupiedLocations is None:
            if location[0] <= 0: return Wall(location)
            if location[0] >= self.width - 1: return Wall(location)

            if location[1] <= 0: return Wall(location)
            if location[1] >= self.height - 1: return Wall(location)

            for food in self.foods:
                if location == food.location:
                    return food

            if self.player != None:
                for segment in self.player.segments:
                    if location == segment:
                        return self.player

            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment:
                        return bot

            return None
        else:
            contents = self.occupiedLocations[location[0]][location[1]]

            return contents
    
    def isOutsideWall(self, location):
        if location[0] < 0: return True
        if location[0] > self.width - 1: return True

        if location[1] < 0: return True
        if location[1] > self.height - 1: return True

        return False

    def isEmpty(self, location):
        content = self.getContents(location)
        return content == None

    def moveFood(self, food):
        food.location = self.randomEmptyLocation

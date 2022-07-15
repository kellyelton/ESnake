import random
import logging
import numpy as np
from random import randint
from . import updateHighScore, AppScreen, Snake, Food, Wall, GameObject
from .controllers import Dylan


class Level:
    @staticmethod
    def default():
        return Level(60, 60, 30, 300, 30)

    def __init__(self, width, height, speed, foodCount, botCount):
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.foods = []
        self.player = None
        self.bots = []
        self.occupiedLocations = None
        self.timeOffset = 0
        self.initialFoodCount = foodCount
        self.initialBotCount = botCount
        self.locations = [[None for x in range(width)] for y in range(height)]
        self.lastUpdateTime = 0

        for i in range(self.initialFoodCount):
            location = self.randomEmptyLocation
            food = Food(location)
            self.updateLocation(food)
            self.foods.append(food)

        self.player = Snake(speed, self.center, ["player"])
        self.updateLocation(self.player)

        self.bestBot = None

        self.bots = []
        for i in range(self.initialBotCount):
            location = self.randomEmptyLocation
            snake = Snake(speed, location, ["bot"], Dylan())
            self.updateLocation(snake)
            self.bots.append(snake)

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
        # TODO: if no empty, then check to the right, if not empty, check right again, etc until we find one.
        # Checking random over and over is likely to cause lots of fails and random slowdowns

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
                storedHighScore = updateHighScore(
                    app.config, self.player.score)
                if storedHighScore:
                    self.logger.debug("Got a high score")

        for bot in self.bots:
            bot.update(app, time, self)

            self.refreshOccupiedLocations()

            if bot.isDead:
                msSincePlayerDied = time - bot.deathTime

                if msSincePlayerDied >= 1000:
                    self.logger.debug("done with death delay")

                    if self.bestBot is None or bot.score > self.bestBot.score:
                        bestScore = "none"
                        if self.bestBot is not None:
                            bestScore = self.bestBot.score
                        self.logger.info(
                            f"Bot got new high score {bot.score} > {bestScore}")
                        self.bestBot = bot

                    if random.random() > 0.5:
                        newController = Dylan(self.bestBot.controller)
                    else:
                        newController = Dylan()

                    newBot = Snake(bot.speed, self.randomEmptyLocation, [
                                   "bot"], newController)

                    self.bots.append(newBot)
                    self.bots.remove(bot)

                    self.refreshOccupiedLocations()

    def updateLocation(self, gameObject: GameObject):
        pass

    def refreshOccupiedLocations(self):
        if self.occupiedLocations is None:
            self.occupiedLocations = np.empty(
                shape=(self.height, self.width), dtype='object')
        else:
            self.occupiedLocations.fill(None)

        for food in self.foods:
            self.occupiedLocations[food.location[0]][food.location[1]] = food

        if self.player is not None:
            for segment in self.player.segments:
                self.occupiedLocations[segment.location[0]
                                       ][segment.location[1]] = self.player

        for bot in self.bots:
            for segment in bot.segments:
                self.occupiedLocations[segment.location[0]
                                       ][segment.location[1]] = bot

        for x in range(self.width):
            self.occupiedLocations[0][x] = Wall((x, 0))
            self.occupiedLocations[self.height -
                                   1][x] = Wall((x, self.height - 1))

        for y in range(self.height):
            self.occupiedLocations[y][0] = Wall((0, y))
            self.occupiedLocations[y][self.width -
                                      1] = Wall((self.width - 1, y))

    def getContents(self, location):
        if self.isOutsideWall(location):
            return None

        if self.occupiedLocations is None:
            if location[0] <= 0:
                return Wall(location)
            if location[0] >= self.width - 1:
                return Wall(location)

            if location[1] <= 0:
                return Wall(location)
            if location[1] >= self.height - 1:
                return Wall(location)

            for food in self.foods:
                if location == food.location:
                    return food

            if self.player is not None:
                for segment in self.player.segments:
                    if location == segment.location:
                        return self.player

            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment.location:
                        return bot

            return None
        else:
            contents = self.occupiedLocations[location[0]][location[1]]

            return contents

    def isOutsideWall(self, location):
        if location[0] < 0:
            return True
        if location[0] > self.width - 1:
            return True

        if location[1] < 0:
            return True
        if location[1] > self.height - 1:
            return True

        return False

    def isEmpty(self, location):
        content = self.getContents(location)
        return content is None

    def moveFood(self, food):
        food.location = self.randomEmptyLocation

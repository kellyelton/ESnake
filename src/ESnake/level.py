import random
import logging
from random import randint
from ESnake.appscreen import AppScreen
from ESnake.snake import Snake
from ESnake.location import Location
from ESnake.modifiers import SpeedBoostFromIntervalModifier

class Level:
    @classmethod
    def default(cls):
        return cls(40, 40, 8)

    def __init__(self, width, height, speed: float):
        self._log = logging.getLogger(__name__)
        self.width = width
        self.height = height

        self.player: Snake = Snake(0, speed, self.center, self)
        self.player.modifiers.append(SpeedBoostFromIntervalModifier(0.25, 20000))

        self.isHighScore = False
        self.foodLocation = None # Needs to exist before we set it to random
        self.foodLocation = self.randomEmptyLocation
        self.startTime: int = None
    
    @property
    def center(self) -> Location:
        return Location(self.width // 2, self.height // 2)

    @property
    def randomLocation(self) -> Location:
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)

        return Location(x, y)
    
    @property
    def randomEmptyLocation(self) -> Location:
        location = self.randomLocation

        while not self.isEmpty(location):
            location = self.randomLocation

        return location
    
    def update(self, app, time):
        if not self.player.state == "dead":
            self.player.update(time)
        else:
            msSincePlayerDied = time - self.player.deathTime

            if msSincePlayerDied >= 3000:
                self._log.debug("done with death delay")
                app.screen = AppScreen.PostGame

    def getContents(self, location: Location):
        if location == self.foodLocation:
            return "food"
        
        for playerLocation in self.player.segments:
            if location == playerLocation:
                return "player"
        
        if location.x <= 0: return "wall"
        if location.x >= self.width - 1: return "wall"

        if location.y <= 0: return "wall"
        if location.y >= self.height - 1: return "wall"

        return None

    def isEmpty(self, location: Location):
        if location == self.foodLocation:
            return False

        for playerSegment in self.player.segments:
            if location == playerSegment:
                return False

        if location.x <= 0 or location.x >= self.width - 1:
            return False
        if location.y <= 0 or location.y >= self.height - 1:
            return False 

        return True

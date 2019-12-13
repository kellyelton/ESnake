import logging
from ESnake.direction import Direction
from ESnake.location import Location
from ESnake.helpers import hasFunction
from ESnake.highscore import getHighScore, updateHighScore

class Snake:
    def __init__(self, id: int, speed: float, location: Location, level):
        self._log = logging.Logger(__name__)
        self.id: int = id
        self.speed: float = speed
        self.speedBoost: float = 0
        self.modifiers: [] = []
        self.segments: [Location] = [location]
        self.score: int = 0
        self.isHighScore: bool = False
        self.direction: Direction = None
        self.nextDirection: Direction = None
        self.state: str = None
        self.spawnTime: int = 0
        self.startTime: int = 0
        self.deathTime: int = 0
        self.lastMoveTime: int = 0
        self.lastEatTime: int = 0
        self.foodEaten: [] = []
        self._level = level
    
    def spawn(self, time: int):
        if time <= 0: raise Exception(f"Invalid spawn time: {time}")
        if not self.state == None: raise Exception(f"Already spawned")

        self.spawnTime = time
        self.state = "spawned"

    def start(self, time: int):
        if time <= 0: raise Exception(f"Invalid start time: {time}")

        if self.state == "spawned":
            if self.spawnTime >= time: raise Exception(f"spawn time {self.spawnTime} is greater than start time {time}")

            self.startTime = time
            self.state = "started"
        elif self.state == None:
            raise Exception(f"Must spawn first")
        elif self.state == "started":
            raise Exception(f"Already started")
        else:
            raise Exception(f"Invalid transition from {self.state} to started")
    
    def kill(self, time: int):
        if time <= 0: raise Exception(f"Invalid kill time: {time}")

        if self.state == "started":
            if self.startTime >= time: raise Exception(f"start time {self.spawnTime} is greater than kill time {time}")

            self.deathTime = time
            self.state = "dead"

        elif self.state == None:
            raise Exception(f"Must spawn and start first")
        elif self.state == "spawned":
            raise Exception("Must start first")
        elif self.state == "dead":
            raise Exception(f"Already dead")
        else:
            raise Exception(f"Invalid transition from {self.state} to dead")

    def update(self, time: int):
        if self.state == None:
            pass
        elif self.state == "spawned":
            pass
        elif self.state == "started":
            self._update_started(time)
        elif self.state == "dead":
            pass
        else:
            raise Exception(f"Invalid state {self.state}")

    def _update_started(self, time: int):
        speedBoost: float = 0

        for modifier in self.modifiers:
            if hasFunction(modifier, "modifySpeed"):
                speedBoost += modifier.modifySpeed(self, time)

        self.speedBoost = speedBoost

        adjustedSpeed = self.speed + self.speedBoost

        minDelay = 1000 / adjustedSpeed

        msSincePlayerLastMoved = time - self.lastMoveTime

        if msSincePlayerLastMoved >= minDelay:
            self.lastMoveTime = time
            self.movePlayer(time)

    def movePlayer(self, time: int):
        newDirection = self.nextDirection
        self.nextDirection = None

        if newDirection != None and self.direction != newDirection:
            # Don't allow reversing if we have a tail
            if len(self.segments) > 1:
                if self.direction.opposite == newDirection:
                    #self.logger.debug(f"Can't move {newDirection}, while player is moving {self.direction}")
                    newDirection = self.direction # cancel out change

            self.direction = newDirection

        if self.direction == None: return

        removeTail = True

        oldLocation = self.segments[0]

        newLocation = oldLocation.getNeighbor(self.direction)

        newLocationContents = self._level.getContents(newLocation)

        if newLocationContents == "food":
            self.score += 1
            self._log.debug(f"eating food. new score {self.score}")
            self._level.foodLocation =  self._level.randomEmptyLocation
            self.foodEaten.append(time)
            self.lastEatTime = time
            removeTail = False
        elif newLocationContents == "player":
            self._log.debug(f"player ran into themselves")
            self.kill(time)
        elif newLocationContents == "wall":
            self._log.debug(f"player ran into a wall")
            self.kill(time)

        self.segments.insert(0, newLocation)

        if removeTail:
            self.segments.pop()

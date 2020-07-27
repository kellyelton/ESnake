import logging
from . import Direction

class Snake:
    def __init__(self, speed, location, controller = None):
        self.logger = logging.getLogger(__name__)
        self.speed = speed
        self.score = 0
        self.startTime = None
        self.direction: Direction = None
        self.requestedDirection: Direction = None
        self.segments = [location]
        self.lastTimeMoved = 0
        self.lastTimeAte = 0
        self.deathTime = 0
        self.isDead = False
        self.controller = controller
    def update(self, app, time, level):
        if not self.isDead:
            if self.startTime == None:
                self.startTime = time

            if not self.controller == None:
                self.controller.update(app, time, self)

            runSeconds = (time - self.startTime) / 1000
            self.speedBoost = runSeconds / 12
            adjustedSpeed = self.speed + self.speedBoost

            minDelay = 1000 / adjustedSpeed

            msSinceLastMoved = time - self.lastTimeMoved

            if msSinceLastMoved >= minDelay:
                self.lastTimeMoved = time
                self.move(app, time, level)

    def move(self, app, time, level):
        newDirection = self.requestedDirection
        self.requestedDirection = None

        if newDirection != None and self.direction != newDirection:
            # Don't allow reversing if we have a tail
            if len(self.segments) > 1:
                if self.direction.opposite == newDirection:
                    #self.logger.debug(f"Can't move {newDirection}, while player is moving {self.playerDirection}")
                    newDirection = self.direction # cancel out change

            self.direction = newDirection

        if self.direction == None: return

        oldHead = self.segments[0]
        newHead = oldHead
        removeTail = True

        if self.direction == Direction.left:
            newHead = (oldHead[0] - 1, oldHead[1])
        elif self.direction == Direction.right:
            newHead = (oldHead[0] + 1, oldHead[1])
        elif self.direction == Direction.up:
            newHead = (oldHead[0], oldHead[1] - 1)
        elif self.direction == Direction.down:
            newHead = (oldHead[0], oldHead[1] + 1)

        newHeadContents = level.getContents(newHead)

        if newHeadContents == "food":
            self.score += 1
            self.logger.debug(f"eating food. new score {self.score}")
            self.lastTimeAte = time
            removeTail = False
            level.moveFood()
        elif newHeadContents == "snake":
            self.logger.debug(f"ran into someone")
            self.isDead = True
            #TODO: kill other dude
            self.deathTime = time
        elif newHeadContents == "wall":
            self.logger.debug(f"ran into a wall")
            self.isDead = True
            self.deathTime = time

        self.segments.insert(0, newHead)

        if removeTail:
            self.segments.pop()

import logging
from . import Direction, GameObject, SnakeSegment

class Snake(GameObject):
    def __init__(self, speed, location, tags, controller = None):
        tags.append("snake")

        super().__init__(tags)

        self.logger = logging.getLogger(__name__)
        self.speed = speed
        self.score = 0
        self.foodScore = 0
        self.energy = 1
        self.startTime = None
        self.direction: Direction = None
        self.previousRequestedDirection: Direction = None
        self.requestedDirection: Direction = None
        self.lastTimeMoved = 0
        self.lastTimeAte = 0
        self.deathTime = 0
        self.isDead = False
        self.tilesTouched = set()
        self.controller = controller
        self.segments = [SnakeSegment(self, location, None)]
    def update(self, app, time, level):
        if not self.isDead:
            if self.startTime == None:
                self.startTime = time

            if not self.controller == None:
                self.controller.update(app, time, level, self)

            runSeconds = (time - self.startTime) / 1000
            self.speedBoost = runSeconds / 12
            adjustedSpeed = self.speed# + self.speedBoost

            msSinceLastMoved = time - self.lastTimeMoved

            if msSinceLastMoved >= adjustedSpeed:
                self.lastTimeMoved = time
                if not self.controller == None:
                    self.controller.move(app, time, level, self)
                self.move(app, time, level)

    def move(self, app, time, level):
        self.tilesTouched.add(self.segments[0].location)

        self.energy = max(0, self.energy - 0.002)

        if self.direction != None: # consume extra energy when moving
            self.energy = max(0, self.energy - 0.01)

        if self.energy == 0 and "player" not in self.tags:
            self.kill(app, time, level, "ran out of energy")
            return

        # Change course
        if self.requestedDirection != None:
            newDirection = self.previousRequestedDirection = self.requestedDirection
            self.requestedDirection = None

            # Switch directions only if we're not already going that direction
            if self.direction != newDirection:
                # Don't allow reversing if we have a tail
                if len(self.segments) > 1:
                    if self.direction is not None:
                        if self.direction.opposite == newDirection:
                            # self.logger.debug(f"Can't move {newDirection}, while player is moving {self.playerDirection}")
                            self.stopDirection = self.direction
                            newDirection = None  # self.direction # cancel out change
                    else:
                        if self.stopDirection.opposite == newDirection:
                            newDirection = None

                self.direction = newDirection
        else:
            self.previousRequestedDirection = self.direction

        if self.direction == None: return

        oldHead = self.segments[0].location
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

        if level.isOutsideWall(newHead): return

        newHeadContents = level.getContents(newHead)

        if(newHeadContents != None):
            if "food" in newHeadContents.tags:
                self.foodScore += 1
                self.logger.info(f"eating food. new food score {self.foodScore}")
                self.lastTimeAte = time
                self.energy = min(1, self.energy + 0.1)
                removeTail = False
                level.moveFood(newHeadContents)
            elif "snake" in newHeadContents.tags:
                if newHeadContents == self:
                    self.logger.info(f"{self} ran into itself")
                else:
                    self.logger.info(f"{self} ran into {newHeadContents}")
                    if newHead == newHeadContents.segments[0].location: # hit other snakes head
                        newHeadContents.kill(app, time, level, self)
                    else: # hit other snakes tail
                        self.logger.info(f"{newHeadContents} scored a kill on {self}")

                self.kill(app, time, level, newHeadContents)
            elif "wall" in newHeadContents.tags:
                self.kill(app, time, level, newHeadContents)

        newSegment = SnakeSegment(self, newHead, self.direction)

        self.segments[0].isHead = False
        self.segments.insert(0, newSegment)

        if removeTail:
            self.segments.pop()

        previousSegmentDirection = self.direction
        for segment in self.segments:
            if segment.direction == previousSegmentDirection: continue

            tpd = segment.direction

            segment.direction = previousSegmentDirection

            previousSegmentDirection = tpd
    
    def kill(self, app, time, level, murderer):
        if self.isDead:
            return

        if self == level.player:
            return  # don't kill player while we're debugging ai

        self.logger.debug(f"{self} killed: {murderer}.")

        self.tileTouchCount = len(self.tilesTouched)
        self.tilesTouched.clear()
        self.tilesTouched = None
        self.isDead = True
        self.deathTime = time
        tilePercent = (self.tileTouchCount / (level.width * level.height))
        tileScore = tilePercent * 50000  # Score for touching lots of tiles

        if self.tileTouchCount <= 5:
            self.score = 0
            return

        foodScore = self.foodScore * 1000

        ageScore = 0
        if self.startTime is not None:
            ageScore = (self.deathTime - self.startTime) / 200

        score = foodScore + tileScore + ageScore

        self.score = int(score)

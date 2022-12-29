import logging
from . import Direction, GameObject, SnakeSegment


class Snake(GameObject):
    def __init__(self, speed, location, tags, controller=None):
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
        self.hunger = 0
        self.deathTime = 0
        self.isDead = False
        self.killCount = 0
        self.tileTouchCount = 0
        self.tilesTouched = set()
        self.controller = controller
        self.segments = [SnakeSegment(self, location, None)]

    def update(self, app, time, level):
        if not self.isDead:
            if self.startTime is None:
                self.startTime = time

            if self.controller is not None:
                self.controller.update(app, time, level, self)

            runSeconds = (time - self.startTime) / 1000
            self.speedBoost = runSeconds / 12
            adjustedSpeed = self.speed  # + self.speedBoost

            msSinceLastMoved = time - self.lastTimeMoved

            if msSinceLastMoved >= adjustedSpeed:
                self.lastTimeMoved = time
                if self.controller is not None:
                    self.controller.move(app, time, level, self)
                self.move(app, time, level)

    def move(self, app, time, level):
        self.tilesTouched.add(self.segments[0].location)
        self.tileTouchCount = len(self.tilesTouched)

        # TODO self.energy = max(0, self.energy - 0.002)

        ageCap = 60 * 10
        maxEnergyDrain = 0.5
        energyDrain = 0.01

        if self.tileTouchCount > 5000:
            maxEnergyDrain = 0.06
        elif self.tileTouchCount > 1000:
            maxEnergyDrain = 0.07
        elif self.tileTouchCount > 500:
            maxEnergyDrain = 0.08
        elif self.tileTouchCount > 100:
            maxEnergyDrain = 0.09
        elif self.tileTouchCount > 50:
            maxEnergyDrain = 0.1
        elif self.tileTouchCount > 10:
            maxEnergyDrain = 0.2
        elif self.tileTouchCount > 5:
            maxEnergyDrain = 0.3

        self.hunger = min(1000, self.hunger + 1)

        # 3 minutes old and greater, max energy drain
        secondsAlive = min(ageCap, (time - self.startTime) / 1000)
        alivePercent = secondsAlive / ageCap

        energyDrain = maxEnergyDrain * alivePercent

        if self.direction is not None:  # consume extra energy when moving
            movementDrain = (energyDrain * 0.5)
            energyDrain = min(1, energyDrain + movementDrain)
        # else:
        #    energyDrain = ((energyDrain * 0.30) * (1 - alivePercent)) + 0.07

        self.energy = max(0, min(1, self.energy - energyDrain))

        if self.energy <= 0 and "player" not in self.tags:
            self.kill(app, time, level, "ran out of energy")
            return

        # Change course
        if self.requestedDirection is not None:
            newDirection \
                = self.previousRequestedDirection \
                = self.requestedDirection
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

        if self.direction is None:
            return

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

        if level.isOutsideWall(newHead):
            return

        newHeadContents = level.getContents(newHead)

        if newHeadContents is not None:
            if "food" in newHeadContents.tags:
                self.foodScore += 1
                self.logger.info(
                    f"eating food. new food score {self.foodScore}")
                self.lastTimeAte = time
                self.hunger = 0
                self.energy = min(1, self.energy + 0.35)
                removeTail = False
                level.moveFood(newHeadContents)
            elif "snake" in newHeadContents.tags:
                if newHeadContents == self:
                    self.logger.info(f"{self} ran into itself")
                else:
                    self.logger.info(f"{self} ran into {newHeadContents}")
                    # hit other snakes head
                    if newHead == newHeadContents.segments[0].location:
                        newHeadContents.kill(app, time, level, self)
                    else:  # hit other snakes tail
                        self.logger.info(
                            f"{newHeadContents} scored a kill on {self}")

                self.kill(app, time, level, newHeadContents)
            elif "wall" in newHeadContents.tags:
                return  # self.kill(app, time, level, newHeadContents)

        newSegment = SnakeSegment(self, newHead, self.direction)

        self.segments[0].isHead = False
        self.segments.insert(0, newSegment)

        if removeTail:
            self.segments.pop()

        previousSegmentDirection = self.direction
        for segment in self.segments:
            if segment.direction == previousSegmentDirection:
                continue

            tpd = segment.direction

            segment.direction = previousSegmentDirection

            previousSegmentDirection = tpd

    def kill(self, app, time, level, murderer):
        if self.isDead:
            return

        if self == level.player:
            return  # don't kill player while we're debugging ai

        if isinstance(murderer, Snake):
            murderer.killCount = murderer.killCount + 1

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

        killBonus = self.killCount * 1000

        ageScore = 0
        if self.startTime is not None:
            ageScore = (self.deathTime - self.startTime) / 200

        score = foodScore + tileScore + ageScore + killBonus

        self.score = int(score)

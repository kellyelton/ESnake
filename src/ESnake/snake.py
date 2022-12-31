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
        self.direction: Direction = Direction.random()
        self.previousRequestedDirection: Direction = None
        self.requestedDirection: Direction = None
        self.lastTimeMoved = 0
        self.lastTimeAte = 0
        self.hunger = 0
        self.deathTime = 0
        self.isDead = False
        self.killCount = 0
        self.controller = controller
        self.segments = [SnakeSegment(self, location, None)]
        self.viewLocations = None
        self.viewLocationsCount = 0
        self.viewContents = None

    def update(self, app, time, level):
        if self.viewLocations is None:
            self.update_view_locations(level)
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
        energyDrain = 0.001

        self.energy = max(0, min(1, self.energy - energyDrain))

        if self.energy <= 0 and "player" not in self.tags:
            self.kill(app, time, level, "ran out of energy")
            return

        # Change course
        if self.requestedDirection is not None:
            self.previousRequestedDirection = self.requestedDirection

            if self.requestedDirection == Direction.left:
                newDirection = self.direction.relativeLeft
            elif self.requestedDirection == Direction.right:
                newDirection = self.direction.relativeRight
            else:
                raise "Invalid requested direction"

            self.direction = newDirection
            self.requestedDirection = None
        else:
            self.previousRequestedDirection = None

        if self.direction is None:
            raise "No direction set"

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
            self.kill(app, time, level, "lost outside map...")
            return

        newHeadContents = level.getContents(newHead)

        if newHeadContents is not None:
            if "food" in newHeadContents.tags:
                self.foodScore += 1
                self.logger.info(
                    f"eating food. new food score {self.foodScore}")
                self.lastTimeAte = time
                self.hunger = 0
                self.energy = 1
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
                self.kill(app, time, level, newHeadContents)

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
        
        self.update_view_locations(level)    

    def kill(self, app, time, level, murderer):
        if self.isDead:
            return

        if self == level.player:
            return  # don't kill player while we're debugging ai

        if isinstance(murderer, Snake):
            murderer.killCount = murderer.killCount + 1

        self.logger.debug(f"{self} killed: {murderer}.")

        #self.tileTouchCount = len(self.tilesTouched)
        #self.tilesTouched.clear()
        #self.tilesTouched = None
        self.isDead = True
        self.deathTime = time
        #tilePercent = (self.tileTouchCount / (level.width * level.height))
        #tileScore = tilePercent * 50000  # Score for touching lots of tiles

        #if self.tileTouchCount <= 5:
        #    self.score = 0
        #    return

        foodScore = self.foodScore# * 1000

        #killBonus = self.killCount * 1000

        #ageScore = 0
        #if self.startTime is not None:
        #    ageScore = (self.deathTime - self.startTime) / 200

        score = foodScore # + tileScore + ageScore + killBonus

        self.score = int(score)
    
    def update_view_locations(self, level):
        head = self.segments[0].location
        self.viewLocationsCount = 3
        if self.direction == Direction.left:
            self.viewLocations = [
                (head[0] - 1, head[1]),
                (head[0], head[1] + 1),
                (head[0], head[1] - 1)
            ]
        elif self.direction == Direction.right:
            self.viewLocations = [
                (head[0] + 1, head[1]),
                (head[0], head[1] - 1),
                (head[0], head[1] + 1)
            ]
        elif self.direction == Direction.up:
            self.viewLocations = [
                (head[0], head[1] - 1),
                (head[0] - 1, head[1]),
                (head[0] + 1, head[1])
            ]
        elif self.direction == Direction.down:
            self.viewLocations = [
                (head[0], head[1] + 1),
                (head[0] + 1, head[1]),
                (head[0] - 1, head[1])
            ]

        self.viewContents = [
            level.getContents(self.viewLocations[0]),
            level.getContents(self.viewLocations[1]),
            level.getContents(self.viewLocations[2])
        ]

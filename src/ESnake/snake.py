import logging
import math

from . import Direction, GameObject, SnakeSegment


class Snake(GameObject):
    def __init__(self, speed, location, tags, controller):
        tags.append("snake")

        super().__init__(tags)

        self.logger = logging.getLogger(__name__)
        self.speed = speed
        self.score = 0
        self.foodScore = 0
        self.energy = 1
        self.startTime = None
        self.direction: Direction = Direction.random()
        self.previousRequestedDirection: Direction = Direction.none()
        self.requestedDirection: Direction = Direction.none()
        self.lastTimeMoved = 0
        self.lastTimeAte = 0
        self.hunger = 0
        self.deathTime = 0
        self.isDead = False
        self.killCount = 0
        self.controller = controller
        self.segments = [SnakeSegment(self, location, Direction.none())]
        self.viewLocations: list = None
        self.viewLocationsCount = 0
        self.viewContents: list = None
        self.view2: list = None
        self.view2Count = 0

    def update(self, app, time, level):
        if self.viewLocations is None:
            self.update_view_locations(level)
        if not self.isDead:
            if self.startTime is None:
                self.startTime = time

            self.controller.update(app, time, level, self)

            runSeconds = (time - self.startTime) / 1000
            self.speedBoost = runSeconds / 12
            adjustedSpeed = self.speed  # + self.speedBoost

            msSinceLastMoved = time - self.lastTimeMoved

            if msSinceLastMoved >= adjustedSpeed:
                self.lastTimeMoved = time
                self.controller.move(app, time, level, self)
                self.move(app, time, level)

    def move(self, app, time, level):
        energyDrain = 0.001

        self.energy = max(0, min(1, self.energy - energyDrain))

        if self.energy <= 0 and "player" not in self.tags:
            self.kill(app, time, level, "ran out of energy")
            return

        # Change course
        if self.requestedDirection != Direction.none():
            self.previousRequestedDirection = self.requestedDirection

            if self.requestedDirection == Direction.left():
                newDirection = self.direction.relativeLeft
            elif self.requestedDirection == Direction.right():
                newDirection = self.direction.relativeRight
            else:
                raise Exception("Invalid requested direction")

            self.direction = newDirection
            self.requestedDirection = Direction.none()
        else:
            self.previousRequestedDirection = Direction.none()

        if self.direction == Direction.none():
            raise Exception("No direction set")

        oldHead = self.segments[0].location
        newHead = oldHead
        removeTail = True

        if self.direction == Direction.left():
            newHead = (oldHead[0] - 1, oldHead[1])
        elif self.direction == Direction.right():
            newHead = (oldHead[0] + 1, oldHead[1])
        elif self.direction == Direction.up():
            newHead = (oldHead[0], oldHead[1] - 1)
        elif self.direction == Direction.down():
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
        if self.direction == Direction.left():
            self.viewLocations = [
                (head[0] - 4, head[1]),
                (head[0], head[1] + 4),
                (head[0], head[1] - 4)
            ]
        elif self.direction == Direction.right():
            self.viewLocations = [
                (head[0] + 4, head[1]),
                (head[0], head[1] - 4),
                (head[0], head[1] + 4)
            ]
        elif self.direction == Direction.up():
            self.viewLocations = [
                (head[0], head[1] - 4),
                (head[0] - 4, head[1]),
                (head[0] + 4, head[1])
            ]
        elif self.direction == Direction.down():
            self.viewLocations = [
                (head[0], head[1] + 4),
                (head[0] + 4, head[1]),
                (head[0] - 4, head[1])
            ]

        self.viewContents = [
            level.getContents(self.viewLocations[0]),
            level.getContents(self.viewLocations[1]),
            level.getContents(self.viewLocations[2])
        ]

        self.view2 = self.get_view_2(level, self.segments[0].location, self.direction, level.view2Distance)
        self.view2Count = len(self.view2)
    
    def get_view_2(self, level, position, direction, distance):
        # relative to the direction it's looking, normalized to face up.
        # ray cast code, looks distance squares left, left-up, up, right-up, right
        # each direction is [distance, direction, reward, punishment]
        # result: [left, left-up, up, right-up, right]

        # get the direction the snake is facing in radians
        if direction == Direction.up():
            # up (0, -1)
            looking_direction = math.atan2(-1, 0)
        elif direction == Direction.down():
            # down (0, 1)
            looking_direction = math.atan2(1, 0)
        elif direction == Direction.left():
            # left (-1, 0)
            looking_direction = math.atan2(0, -1)
        elif direction == Direction.right():
            # right (1, 0)
            looking_direction = math.atan2(0, 1)

        # get the position of the snake's head
        head_x = position[0]
        head_y = position[1]

        raycasts = [
            [math.atan2(-1, 0), 0, 0, 0],
            [math.atan2(-1, 1), 0, 0, 0],
            [math.atan2(0, 1), 0, 0, 0],
            [math.atan2(1, 1), 0, 0, 0],
            [math.atan2(1, 0), 0, 0, 0]
        ]

        for i, raycast in enumerate(raycasts):
            raycast_direction = raycast[0] 

            dv = (direction.x, direction.y)

            # rotate dv by the raycast direction
            nd = (
                dv[0] * math.cos(raycast_direction) - dv[1] * math.sin(raycast_direction),
                dv[0] * math.sin(raycast_direction) + dv[1] * math.cos(raycast_direction)
            )

            # cast to int, but round to ceil
            # if negative, round to floor
            normalized_direction = (
                round(nd[0]),
                round(nd[1])
            )
            
            # get the position of the first square in the direction
            x = head_x + normalized_direction[0]
            y = head_y + normalized_direction[1]

            # ray cast in the direction
            for d in range(distance):
                entity = level.getContents((x, y))
                if entity is not None:
                    # 0 being farthest away, 1 being closest
                    edistance = 1 - ((d + 1) / distance)
                    raycasts[i][1] = edistance
                    
                    if "wall" in entity.tags:
                        raycasts[i][2] = 0
                        raycasts[i][3] = 1
                    elif "food" in entity.tags:
                        raycasts[i][2] = 1
                        raycasts[i][3] = 0
                    else:
                        raycasts[i][2] = 0
                        raycasts[i][3] = 1

                    break
                x += normalized_direction[0]
                y += normalized_direction[1]
            else:
                raycasts[i][1] = 0
                raycasts[i][2] = 0
                raycasts[i][3] = 0
            
        return raycasts
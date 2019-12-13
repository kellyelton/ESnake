import math
from ESnake.snake import Snake

class SpeedBoostFromIntervalModifier:
    def __init__(self, boost: int, intervalMs: int):
        if boost <= 0: raise Exception(f"boost {boost} is invalid")
        if intervalMs <= 0: raise Exception(f"intervalMs {intervalMs} is invalid")

        self.boost: int = boost
        self.intervalMs: int = intervalMs

    def modifySpeed(self, snake: Snake, time: int):
        runTime = time - snake.startTime

        speedLevel = math.floor(runTime / self.intervalMs)
        
        speedBoost = speedLevel * self.boost

        return speedBoost

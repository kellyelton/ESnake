import logging
import enum
from ESnake.level import Level
from ESnake.snake import Snake

class NoLevel(BaseException): pass

class InvalidState(BaseException): pass

class AlreadyStarted(BaseException): pass

Initialized = "initialized"
Started = "started"

class Session:
    def __init__(self):
        self.__level: Level = None
        self.__state: str = Initialized
        self.__log = logging.getLogger(__name__)

    @property
    def level(self) -> Level: return self.__level

    @level.setter
    def level(self, value):
        if value == None: raise InvalidState(f"None is not a valid Level")
        if not self.__level == value:
            self.__level = value 

    @property
    def State(self) -> str: return self.__state

    @State.setter
    def State(self, value : State):
        if value == None: raise InvalidState("None is not a valid State")
        if self.__state == value: raise InvalidState(f"Cannot transition State from {self.__state} to {value}")
        self.__state = value

    @property
    def Snakes(self) -> []: self.__snakes.values()

    def addSnake(self, snake: Snake):
        if snake == None: raise Exception("snake must be set")

        if snake.id in self.__snakes: raise Exception(f"snake {snake.id} already added")

        self.__snakes[snake.id] = snake

    def removeSnake(self, id: int):
        if self.__snakes.pop(id) == None:
            raise Exception(f"snake {id} doesn't exist")
import enum
import logging
from . import AppScreen, Debug
from .update import versiontuple

class App:
    @property
    def state(self): return self.__state

    @state.setter
    def state(self, value):
        self.logger.info(value)
        self.__state = value

    def __init__(self, engine, config, exelocation, debug : Debug):
        self.logger = logging.getLogger(__name__)
        self.name = "ESnake"
        self.version = versiontuple("0.1.16.0")
        self.exelocation = exelocation
        self.__state = ""
        self.screen = AppScreen.Loading
        self.config = config
        self.engine = engine
        self.debug : Debug = debug

    def run(self):
        try:
            self.state = "initializing"
            self.engine.init(self)

            self.state = "running"
            self.engine.run(self)
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"
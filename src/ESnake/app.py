import enum
import logging
from ESnake.appscreen import AppScreen
from ESnake.level import Level
from ESnake.debug import Debug
from ESnake.update import versiontuple
import ESnake.session as session

class App:
    @property
    def state(self): return self.__state

    @state.setter
    def state(self, value):
        self.logger.info(value)
        self.__state = value

    @property
    def session(self) -> session.Session: return self.__session

    def __init__(self, engine, config, exelocation, debug : Debug):
        self.logger = logging.getLogger(__name__)
        self.name = "ESnake"
        self.version = versiontuple("0.1.16.0")
        self.exelocation = exelocation
        self.__state = ""
        self.__session: session.Session = None
        self.screen: AppScreen = AppScreen.Loading
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

    def newGame(self, level: Level = None):
        if level == None:
            level = Level.default()

        self.__session = session.Session()

        self.__session.level = level

        self.screen = AppScreen.InGame

    def stop(self):
        self.state = "stopping"
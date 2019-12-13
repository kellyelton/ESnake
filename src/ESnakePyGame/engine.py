import pygame
import logging
from ESnake.helpers import hasFunction
from ESnake.level import Level
from ESnake.session import Session
from ESnake.update import versiontuple
from ESnakePyGame.config import Config
from ESnakePyGame.screen import Screen
from ESnakePyGame.style import Style, loadStyle

class PyGameEngine:
    def __init__(self, appname: str, appversion: versiontuple, config: Config, exelocation: str):
        self._log = logging.getLogger(__name__)

        self._log.debug("init")

        self._screen: Screen = None
        self._nextScreen: Screen = Screen.Loading
        self._screenEngine = None
        self._session: Session = None
        self._previousAppScreen = None
        self._config: Config = config
        self._style: Style = loadStyle(self._config.style)
        self._name: str = appname
        self._version: versiontuple = appversion
        self._shutdown: bool = False
        self._exelocation: str = exelocation

        pygame.init()

    @property
    def name(self) -> str: return self._name

    @property
    def version(self) -> versiontuple: return self._version

    @property
    def config(self) -> Config: return self._config

    @property
    def style(self) -> Style: return self._style

    @property
    def session(self) -> Session: return self._session

    @property
    def screen(self) -> Screen: return self._screen

    @property
    def exelocation(self) -> str: return self._exelocation

    @screen.setter
    def screen(self, screen: Screen):
        if screen == None: raise Exception(f"Can't set screen to None")

        if self.screen == screen: return

        self._nextScreen = screen

    @property
    def screenEngine(self): return self._screenEngine

    def run(self):
        self._log.debug("run")

        if self.config.fullscreen:
            self._log.debug("Setting display to FullScreen")

            pyscreen = pygame.display.set_mode(self.config.screenSize, pygame.FULLSCREEN)
        else:
            pyscreen = pygame.display.set_mode(self.config.screenSize)

        pygame.display.set_caption(self.name + f" - v{self.version[0]}.{self.version[1]}.{self.version[2]}")

        clock = pygame.time.Clock()

        self._log.debug("entering run loop")

        try:
            while not self._shutdown:
                time = pygame.time.get_ticks()

                self.configureScreenEngine()
                self.processEvents()
                self.screenEngine.update(time)
                self.draw(pyscreen, time)

                # max fps 60
                # TODO: Something tells me this isn't quite right
                clock.tick(self.config.maxfps)
        finally:
            self._log.debug("exiting run loop")

    def processEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
            elif self._screenEngine == None:
                self._log.debug(f"skipping event {event}");
            else:
                self._log.debug(f"processing event {event}");
                self._screenEngine.processEvent(event)

    def draw(self, pyscreen, time: int):
        if self._screenEngine == None:
            pass
        else:
            self._screenEngine.draw(pyscreen, time)

        ## flip buffer
        pygame.display.flip()

    def configureScreenEngine(self):
        if self._nextScreen == None: return

        self._previousAppScreen = self._screen

        self._screen = self._nextScreen

        self._nextScreen = None

        oldScreenEngine = self._screenEngine
        self._screenEngine = self.createScreenEngine(self._screen)

        if oldScreenEngine != None:
            if hasFunction(oldScreenEngine, "stop"):
                oldScreenEngine.stop()

        self._log.debug(f"Screen Engine changed to {self._screenEngine}")
        
        if hasFunction(self.screenEngine, "start"):
            time = pygame.time.get_ticks()
            self.screenEngine.start(time)

    def createScreenEngine(self, screen: Screen):
        # Imported inside of this method to avoid circular dependancy with PyGameEngine
        import ESnakePyGame.loadingscreen
        import ESnakePyGame.ingamescreen
        import ESnakePyGame.postgamescreen

        if screen == Screen.Loading:
            return ESnakePyGame.loadingscreen.PyLoadingScreenEngine(self)
        elif screen == Screen.InGame:
            return ESnakePyGame.ingamescreen.PyInGameScreenEngine(self)
        elif screen == Screen.PostGame:
            return ESnakePyGame.postgamescreen.PyPostGameScreenEngine(self)
        else:
            raise Exception("Not Implemented")

    def newGame(self, level: Level = None):
        if level == None:
            level = Level.default()

        self._session = Session()

        self._session.level = level

        self.screen = Screen.InGame
    
    def shutdown(self):
        self._log.info("shutdown")
        self._shutdown = True
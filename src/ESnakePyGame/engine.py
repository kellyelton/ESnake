import pygame
import logging
from ESnake import loadStyle, hasFunction, AppScreen, Level
from . import PyLoadingScreenEngine, PyInGameScreenEngine, PyPostGameScreenEngine

class PyGameEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def init(self, app):
        self.logger.debug("init")

        self._screenEngine = None
        self._previousAppScreen = None
        self.style = loadStyle(app.config.style)

        pygame.init()

    @property
    def screenEngine(self): return self._screenEngine

    @screenEngine.setter
    def screenEngine(self, screenEngine):
        self.logger.debug(f"Screen Engine changed to {screenEngine}")

        if self._screenEngine != None:
            if hasFunction(self._screenEngine, "stop"):
                self._screenEngine.stop()

        self._screenEngine = screenEngine

    def run(self, app):
        self.logger.debug("run")

        if app.config.fullscreen:
            self.logger.debug("Setting display to FullScreen")

            pyscreen = pygame.display.set_mode(app.config.screenSize, pygame.FULLSCREEN)
        else:
            pyscreen = pygame.display.set_mode(app.config.screenSize)

        pygame.display.set_caption(app.name)

        clock = pygame.time.Clock()

        self.logger.debug("entering run loop")

        try:
            while app.state == "running":
                self.configureScreenEngine(app)
                self.processEvents(app)
                self.screenEngine.update(app)
                self.draw(app, pyscreen)

                # max fps 60
                clock.tick(app.config.maxfps)
        finally:
            self.logger.debug("exiting run loop")

    def processEvents(self, app):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.stop()
            elif self._screenEngine == None:
                self.logger.debug(f"skipping event {event}");
            else:
                self.logger.debug(f"processing event {event}");
                self._screenEngine.processEvent(app, event)

    def draw(self, app, pyscreen):
        if self._screenEngine == None:
            pass
        else:
            self._screenEngine.draw(app, pyscreen)

        ## flip buffer
        pygame.display.flip()

    def configureScreenEngine(self, app):
        if self._previousAppScreen == app.screen: return

        self._previousAppScreen = app.screen

        self.screenEngine = self.createScreenEngine(app, app.screen)

    def createScreenEngine(self, app, appScreen: AppScreen):
        if app.screen == AppScreen.Loading:
            return PyLoadingScreenEngine(app)
        elif app.screen == AppScreen.InGame:
            level = Level.default()

            return PyInGameScreenEngine(app, level)
        elif app.screen == AppScreen.PostGame:
            previousEngine = self._screenEngine

            level = previousEngine.level

            return PyPostGameScreenEngine(app, level)
        else:
            raise Exception("Not Implemented")
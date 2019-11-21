import pygame
from ..helpers import *
from ..appscreen import AppScreen
from ..level import Level
from .loadingscreen import PyLoadingScreenEngine
from .ingamescreen import PyInGameScreenEngine
from .postgamescreen import PyPostGameScreenEngine
from .Styles import *

class PyGameEngine:
    def init(self, app):
        print("engine init")

        self._screenEngine = None
        self._previousAppScreen = None
        self.style = loadStyle(app.config.style)

        pygame.init()

    @property
    def screenEngine(self): return self._screenEngine

    @screenEngine.setter
    def screenEngine(self, screenEngine):
        if self._screenEngine != None:
            if hasFunction(self._screenEngine, "stop"):
                self._screenEngine.stop()

        self._screenEngine = screenEngine

    def run(self, app):
        print("engine run")

        pyscreen = pygame.display.set_mode(app.config.screenSize)

        pygame.display.set_caption(app.name)

        clock = pygame.time.Clock()

        while app.state == "running":
            self.configureScreenEngine(app)
            self.processEvents(app)
            self.screenEngine.update(app)
            self.draw(app, pyscreen)

            # max fps 60
            clock.tick(app.config.maxfps)

    def processEvents(self, app):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.stop()
            elif self._screenEngine == None:
                print(f"SKIPPING EVENT {event}")
            else:
                print(f"processing {event}")
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
            level = Level(100, 100)

            return PyInGameScreenEngine(app, level)
        elif app.screen == AppScreen.PostGame:
            previousEngine = self._screenEngine

            level = previousEngine.level

            return PyPostGameScreenEngine(app, level)
        else:
            raise Exception("Not Implemented")
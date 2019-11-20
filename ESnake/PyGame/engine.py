import pygame
from ..helpers import *
from ..appscreen import AppScreen
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

    def setScreenEngine(self, screenEngine):
        if self._screenEngine != None:
            if hasFunction(self._screenEngine, "stop"):
                self._screenEngine.stop()

        self._screenEngine = screenEngine

    def updateScreenEngine(self, app):
        if self._previousAppScreen == app.screen: return

        self._previousAppScreen = app.screen

        if app.screen == AppScreen.Loading:
            self.setScreenEngine(PyLoadingScreenEngine())
        elif app.screen == AppScreen.InGame:
            self.setScreenEngine(PyInGameScreenEngine())
        elif app.screen == AppScreen.PostGame:
            self.setScreenEngine(PyPostGameScreenEngine())
        else:
            raise Exception("Not Implemented")

    def run(self, app):
        print("engine run")

        pyscreen = pygame.display.set_mode(app.config.screenSize)

        pygame.display.set_caption(app.name)

        clock = pygame.time.Clock()

        while app.state == "running":
            self.updateScreenEngine(app)
            self.processEvents(app)
            app.updateComponents()
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
import pygame
from .helpers import *
from .appscreen import AppScreen

class PyGameEngine:
    def init(self, app):
        print("engine init")

        self._screenEngine = None
        self._previousAppScreen = None

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

class PyLoadingScreenEngine:
    def __init__(self):
        self.__count = 0

    def processEvent(self, app, event):
        pass

    def draw(self, app, pyscreen):
        self.__count += 1
        if self.__count >= 240:
            app.screen = AppScreen.InGame
            self.__count = 0

        pyscreen.fill(app.style.loadingBackgroundColor)

class PyInGameScreenEngine:
    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                app.player.direction = "left"
            elif event.key == pygame.K_RIGHT:
                app.player.direction = "right"
            elif event.key == pygame.K_UP:
                app.player.direction = "up"
            elif event.key == pygame.K_DOWN:
                app.player.direction = "down"
            elif event.key == pygame.K_ESCAPE:
                app.screen = AppScreen.PostGame
    def draw(self, app, pyscreen):
        pyscreen.fill(app.style.gameBackgroundColor)

        ## TODO: Draw stuff

class PyPostGameScreenEngine:
    def processEvent(self, app, event):
        pass
    def draw(self, app, pyscreen):
        pyscreen.fill(app.style.postGameBackgroundColor)

        ## TODO: Draw stuff
import pygame
from .helpers import *
from .gamescreen import GameScreen

class PyGameEngine:
    def init(self, game):
        print("engine init")

        self._screenEngine = None
        self._previousGameScreen = None

        pygame.init()

    def setScreenEngine(self, screenEngine):
        if self._screenEngine != None:
            if hasFunction(self._screenEngine, "stop"):
                self._screenEngine.stop()

        self._screenEngine = screenEngine

    def updateScreenEngine(self, game):
        if self._previousGameScreen == game.screen: return

        self._previousGameScreen = game.screen

        if game.screen == GameScreen.Loading:
            self.setScreenEngine(PyLoadingScreenEngine())
        elif game.screen == GameScreen.InGame:
            self.setScreenEngine(PyInGameScreenEngine())
        elif game.screen == GameScreen.PostGame:
            self.setScreenEngine(PyPostGameScreenEngine())
        else:
            raise Exception("Not Implemented")

    def run(self, game):
        print("engine run")

        pyscreen = pygame.display.set_mode(game.config.screenSize)

        pygame.display.set_caption(game.name)

        clock = pygame.time.Clock()

        while game.state == "running":
            self.updateScreenEngine(game)
            self._screenEngine.onFrame(game)
            self.processEvents(game)
            game.updateComponents()
            self.draw(game, pyscreen)

            # max fps 60
            clock.tick(game.config.maxfps)

    def processEvents(self, game):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.stop()
            elif self._screenEngine == None:
                print(f"SKIPPING EVENT {event}")
            else:
                print(f"processing {event}")
                self._screenEngine.processEvent(game, event)

    def draw(self, game, pyscreen):
        if self._screenEngine == None:
            pass
        else:
            self._screenEngine.draw(game, pyscreen)

        ## flip buffer
        pygame.display.flip()

class PyLoadingScreenEngine:
    def __init__(self):
        self.__count = 0

    def onFrame(self, game):
        self.__count += 1
        if self.__count >= 240:
            game.screen = GameScreen.InGame
            self.__count = 0

    def processEvent(self, game, event):
        pass

    def draw(self, game, pyscreen):
        pyscreen.fill(game.style.loadingBackgroundColor)

class PyInGameScreenEngine:
    def onFrame(self, game):
        pass
    def processEvent(self, game, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.player.direction = "left"
            elif event.key == pygame.K_RIGHT:
                game.player.direction = "right"
            elif event.key == pygame.K_UP:
                game.player.direction = "up"
            elif event.key == pygame.K_DOWN:
                game.player.direction = "down"
            elif event.key == pygame.K_ESCAPE:
                game.screen = GameScreen.PostGame
    def draw(self, game, pyscreen):
        pyscreen.fill(game.style.gameBackgroundColor)

        ## TODO: Draw stuff

class PyPostGameScreenEngine:
    def onFrame(self, game):
        pass
    def processEvent(self, game, event):
        pass
    def draw(self, game, pyscreen):
        pyscreen.fill(game.style.postGameBackgroundColor)

        ## TODO: Draw stuff
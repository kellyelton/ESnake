import pygame
from ESnake import *

class PyLoadingScreenEngine:
    def __init__(self, app):
        self.__count = 0
        self.__dotCount = 0
        self.__font = pygame.font.Font(app.engine.style.loadingScreenFont, app.engine.style.loadingScreenFontSize)
        self.__lastUpdateDotsTime = 0

    def processEvent(self, app, event): pass
    def update(self, app): pass

    def draw(self, app, pyscreen):
        self.__count += 1
        if self.__count >= 100:
            app.screen = AppScreen.InGame
            self.__count = 0

        now = pygame.time.get_ticks()

        msSinceLastDotUpdate = now - self.__lastUpdateDotsTime
        
        if msSinceLastDotUpdate > 500:
            self.__dotCount += 1
            if self.__dotCount == 4:
                self.__dotCount = 0

            self.__lastUpdateDotsTime = pygame.time.get_ticks()

        loadingString = "Loading"
        for _ in range(self.__dotCount):
            loadingString += "."

        pyscreen.fill(app.engine.style.loadingBackgroundColor)

        text = self.__font.render(loadingString, True, app.engine.style.loadingTextColor)

        textRect = text.get_rect()
        textRect.center = pyscreen.get_rect().center

        pyscreen.blit(text, textRect)
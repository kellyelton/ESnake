import pygame
from ..appscreen import AppScreen

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
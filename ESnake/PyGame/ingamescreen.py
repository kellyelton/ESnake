import pygame
from ..appscreen import AppScreen

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
        pyscreen.fill(app.engine.style.gameBackgroundColor)

        ## TODO: Draw stuff
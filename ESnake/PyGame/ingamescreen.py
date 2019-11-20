import pygame
from ..appscreen import AppScreen

class PyInGameScreenEngine:
    def __init__(self, app):
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)

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

        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen)
        self.drawScore(app, pyscreen)

    def drawPlayer(self, app, pyscreen):
        pass

    def drawFood(self, app, pyscreen):
        pass

    def drawScore(self, app, pyscreen):
        text = self.__scoreFont.render(str(app.score), True, app.engine.style.inGameScoreTextColor)

        textRect = text.get_rect()
        textRect.topright = pyscreen.get_rect().topright

        textRect.left -= 10
        textRect.top += 10

        pyscreen.blit(text, textRect)
import pygame
from ..appscreen import AppScreen

class PyInGameScreenEngine:
    def __init__(self, app):
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                app.level.playerDirection = "left"
            elif event.key == pygame.K_RIGHT:
                app.level.playerDirection = "right"
            elif event.key == pygame.K_UP:
                app.level.playerDirection = "up"
            elif event.key == pygame.K_DOWN:
                app.level.playerDirection = "down"
            elif event.key == pygame.K_ESCAPE:
                app.screen = AppScreen.PostGame

    def draw(self, app, pyscreen):
        pyscreen.fill(app.engine.style.gameBackgroundColor)

        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen)
        self.drawScore(app, pyscreen)

    def drawPlayer(self, app, pyscreen):
        playerLeft = app.level.playerLocation[0] * app.level.tileSize[0]
        playerTop = app.level.playerLocation[1] * app.level.tileSize[1]
        playerWidth = app.level.tileSize[0]
        playerHeight = app.level.tileSize[1]

        drawLocation = (playerLeft, playerTop, playerWidth, playerHeight)

        pygame.draw.rect(pyscreen, app.engine.style.playerColor, drawLocation)

    def drawFood(self, app, pyscreen):
        pass

    def drawScore(self, app, pyscreen):
        text = self.__scoreFont.render(str(app.score), True, app.engine.style.inGameScoreTextColor)

        textRect = text.get_rect()
        textRect.topright = pyscreen.get_rect().topright

        textRect.left -= 10
        textRect.top += 10

        pyscreen.blit(text, textRect)
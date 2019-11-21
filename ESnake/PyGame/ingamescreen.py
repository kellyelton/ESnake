import pygame
from ..appscreen import AppScreen

class PyInGameScreenEngine:
    def __init__(self, app, level):
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)
        self.__level = level

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.__level.playerDirection = "left"
            elif event.key == pygame.K_RIGHT:
                self.__level.playerDirection = "right"
            elif event.key == pygame.K_UP:
                self.__level.playerDirection = "up"
            elif event.key == pygame.K_DOWN:
                self.__level.playerDirection = "down"
            elif event.key == pygame.K_ESCAPE:
                app.screen = AppScreen.PostGame
    
    def update(self, app):
        now = pygame.time.get_ticks()

        self.__level.update(app, now)

    def draw(self, app, pyscreen):
        pyscreen.fill(app.engine.style.gameBackgroundColor)

        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen)
        self.drawScore(app, pyscreen)
    
    def getLocationRect(self, app, pyscreen, location):
        size = pyscreen.get_size()
        tileWidth = size[0] / self.__level.width
        tileHeight = size[1] / self.__level.height

        tileWidth = int(tileWidth)
        tileHeight = int(tileHeight)

        minsize = min(tileWidth, tileHeight)

        tileWidth = minsize
        tileHeight = minsize

        x = location[0] * tileWidth
        y = location[1] * tileHeight

        return (x, y, tileWidth, tileHeight)

    def drawPlayer(self, app, pyscreen):
        if not self.__level.isPlayerDead:
            for playerLocation in self.__level.playerLocations:
                drawLocation = self.getLocationRect(app, pyscreen, playerLocation)

                pygame.draw.rect(pyscreen, app.engine.style.playerColor, drawLocation, 0)
        else:
            for playerLocation in self.__level.playerLocations:
                drawLocation = self.getLocationRect(app, pyscreen, playerLocation)

                pygame.draw.rect(pyscreen, app.engine.style.playerDeadColor, drawLocation, 0)


    def drawFood(self, app, pyscreen):
        drawLocation = self.getLocationRect(app, pyscreen, self.__level.foodLocation)

        pygame.draw.rect(pyscreen, app.engine.style.foodColor, drawLocation, 0)

    def drawScore(self, app, pyscreen):
        text = self.__scoreFont.render(str(self.__level.score), True, app.engine.style.inGameScoreTextColor)

        textRect = text.get_rect()
        textRect.topright = pyscreen.get_rect().topright

        textRect.left -= 10
        textRect.top += 10

        pyscreen.blit(text, textRect)
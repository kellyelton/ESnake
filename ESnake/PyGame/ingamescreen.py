import pygame
from ..appscreen import AppScreen

class PyInGameScreenEngine:
    def __init__(self, app, level):
        self.__debugFont = pygame.font.SysFont("Lucida Console", 14)
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)
        self.__level = level

    @property
    def level(self): return self.__level

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            canMoveBackwards = len(self.__level.playerLocations) == 1

            if event.key == pygame.K_LEFT:
                if canMoveBackwards or self.__level.playerDirection != "right":
                    self.__level.playerDirection = "left"
            elif event.key == pygame.K_RIGHT:
                if canMoveBackwards or self.__level.playerDirection != "left":
                    self.__level.playerDirection = "right"
            elif event.key == pygame.K_UP:
                if canMoveBackwards or self.__level.playerDirection != "down":
                    self.__level.playerDirection = "up"
            elif event.key == pygame.K_DOWN:
                if canMoveBackwards or self.__level.playerDirection != "up":
                    self.__level.playerDirection = "down"
            elif event.key == pygame.K_ESCAPE:
                app.screen = AppScreen.PostGame
    
    def update(self, app):
        now = pygame.time.get_ticks()

        self.__level.update(app, now)

    def draw(self, app, pyscreen):
        pyscreen.fill(app.engine.style.gameBackgroundColor)

        self.drawBorder(app, pyscreen)
        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen)
        self.drawScore(app, pyscreen)
        
    def drawBorder(self, app, pyscreen):
        borderColor = (255, 255, 255)

        tileSize = self.getTileSize(pyscreen)

        playRect = self.getPlayRectangle(pyscreen)

        topRect = pygame.Rect(playRect.topleft, (playRect.width, tileSize))
        leftRect = pygame.Rect(playRect.topleft, (tileSize, playRect.height))
        rightRect = pygame.Rect((playRect.topright[0] - tileSize, playRect.topright[1]), (tileSize, playRect.height))
        bottomRect = pygame.Rect((playRect.bottomleft[0], playRect.bottomleft[1] - tileSize), (playRect.width, tileSize))

        pygame.draw.rect(pyscreen, borderColor, topRect, 0)
        pygame.draw.rect(pyscreen, borderColor, leftRect, 0)
        pygame.draw.rect(pyscreen, borderColor, rightRect, 0)
        pygame.draw.rect(pyscreen, borderColor, bottomRect, 0)

    def drawPlayer(self, app, pyscreen):
        isFirstSection = True
        for playerLocation in self.__level.playerLocations:
            drawLocation = self.getLocationRect(app, pyscreen, playerLocation)

            if isFirstSection and self.__level.isPlayerDead:
                pygame.draw.rect(pyscreen, app.engine.style.playerDeadColor, drawLocation, 0)
            else:
                pygame.draw.rect(pyscreen, app.engine.style.playerColor, drawLocation, 0)

            isFirstSection = False

            if app.debug.playerLocation:
                string = f"{playerLocation[0]}, {playerLocation[1]}"
                text = self.__debugFont.render(string, True, (255, 0, 0), (255, 255, 255))

                textRect = text.get_rect()
                textRect.topleft = (drawLocation[0], drawLocation[1])

                pyscreen.blit(text, textRect)

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

    def getTileSize(self, pyscreen):
        size = pyscreen.get_size()

        # padding
        size = (size[0] - 10, size[1] - 10)

        tileWidth = size[0] / self.__level.width
        tileHeight = size[1] / self.__level.height

        tileWidth = int(tileWidth)
        tileHeight = int(tileHeight)

        return min(tileWidth, tileHeight)

    def getPlayRectangle(self, pyscreen):
        tileSize = self.getTileSize(pyscreen)

        rect = pygame.Rect(0, 0, self.__level.width * tileSize, self.__level.height * tileSize)

        rect.center = pyscreen.get_rect().center

        return rect
    
    def getLocationRect(self, app, pyscreen, location):
        playRect = self.getPlayRectangle(pyscreen)
        tileSize = self.getTileSize(pyscreen)

        x = (location[0] * tileSize) + playRect.x
        y = (location[1] * tileSize) + playRect.y

        return (x, y, tileSize, tileSize)
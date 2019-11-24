import pygame
from ..appscreen import AppScreen
from ..direction import Direction
from ..level import Level
from ..app import App

class PyInGameScreenEngine:
    def __init__(self, app: App, level: Level):
        self.__debugFont = pygame.font.SysFont("Lucida Console", 14)
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)
        self.__statsFont = pygame.font.Font(app.engine.style.inGameStatsFont, app.engine.style.inGameStatsFontSize)
        #TODO: Make this self.level
        self.__level: Level = level
        self.__playerDeadSections: int = 0
        self.__lastDeadSectionAdded: int = 0

    @property
    def level(self): return self.__level

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.__level.requestedPlayerDirection = Direction.left
            elif event.key == pygame.K_RIGHT:
                self.__level.requestedPlayerDirection = Direction.right
            elif event.key == pygame.K_UP:
                self.__level.requestedPlayerDirection = Direction.up
            elif event.key == pygame.K_DOWN:
                self.__level.requestedPlayerDirection = Direction.down
            elif event.key == pygame.K_ESCAPE:
                app.screen = AppScreen.PostGame
    
    def update(self, app):
        now = pygame.time.get_ticks()

        self.__level.update(app, now)

    def draw(self, app, pyscreen):
        now = pygame.time.get_ticks()

        pyscreen.fill(app.engine.style.gameBackgroundColor)

        self.drawBorder(app, pyscreen)
        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen, now)
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

    def drawPlayer(self, app, pyscreen, now):
        if self.__level.isPlayerDead:
            text = self.__scoreFont.render("RIP", True, app.engine.style.playerDeadColor)

            textRect = text.get_rect()
            textRect.center = pyscreen.get_rect().center

            pyscreen.blit(text, textRect)

            timeSinceLastDeadSegment = now - self.__lastDeadSectionAdded
            if timeSinceLastDeadSegment >= 100:
                self.__lastDeadSectionAdded = now
                self.__playerDeadSections += 1

        playerSegmentCount = len(self.__level.playerLocations)
        for index, playerLocation in enumerate(reversed(self.__level.playerLocations)):
            fillColor = app.engine.style.playerColor

            if self.__level.isPlayerDead:
                if index >= playerSegmentCount - self.__playerDeadSections:
                    fillColor = app.engine.style.playerDeadColor

            drawLocation = self.getLocationRect(app, pyscreen, playerLocation)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

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
        text = self.__scoreFont.render(str("Score"), True, app.engine.style.inGameScoreTextColor)

        labelTextRect = text.get_rect()
        labelTextRect.topright = pyscreen.get_rect().topright

        labelTextRect.left -= 5
        labelTextRect.top += 5

        pyscreen.blit(text,labelTextRect)

        text = self.__scoreFont.render(str(self.__level.score), True, app.engine.style.inGameScoreTextColor)

        scoreTextRect = text.get_rect()
        scoreTextRect .topright = labelTextRect.bottomright

        pyscreen.blit(text, scoreTextRect)

        string = f"{self.__level.playerSpeed} + {self.__level.playerSpeedBoost:0.2f} t/s"
        text = self.__statsFont.render(string, True, app.engine.style.inGameStatsTextColor)

        textRect = text.get_rect()
        textRect.topright = scoreTextRect.bottomright

        textRect .top += 5

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
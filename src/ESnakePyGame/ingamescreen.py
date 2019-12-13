import pygame
import logging
from ESnake import Direction, AppScreen, App, Level

class PyInGameScreenEngine:
    def __init__(self, app: App):
        self.logger = logging.getLogger(__name__)
        self.__debugFont = pygame.font.SysFont("Lucida Console", 14)
        self.__scoreFont = pygame.font.Font(app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)
        self.__statsFont = pygame.font.Font(app.engine.style.inGameStatsFont, app.engine.style.inGameStatsFontSize)
        self.__playerDeadSections: int = 0
        self.__lastDeadSectionAdded: int = 0

    def processEvent(self, app: App, event):
        level = app.session.level

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.logger.debug("Requested Direction changed to Left");
                level.requestedPlayerDirection = Direction.left
            elif event.key == pygame.K_RIGHT:
                self.logger.debug("Requested Direction changed to Right");
                level.requestedPlayerDirection = Direction.right
            elif event.key == pygame.K_UP:
                self.logger.debug("Requested Direction changed to Up");
                level.requestedPlayerDirection = Direction.up
            elif event.key == pygame.K_DOWN:
                self.logger.debug("Requested Direction changed to Down");
                level.requestedPlayerDirection = Direction.down
            elif event.key == pygame.K_ESCAPE:
                self.logger.debug("esc pressed, switch to post game");
                app.screen = AppScreen.PostGame
    
    def update(self, app: App):
        now = pygame.time.get_ticks()

        app.session.level.update(app, now)

    def draw(self, app: App, pyscreen):
        now = pygame.time.get_ticks()

        pyscreen.fill(app.engine.style.gameBackgroundColor)

        self.drawBorder(app, pyscreen)
        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen, now)
        self.drawScore(app, pyscreen)
        
    def drawBorder(self, app: App, pyscreen):
        level = app.session.level

        borderColor = app.engine.style.inGameWallColor

        tileSize = self.getTileSize(level, pyscreen)

        playRect = self.getPlayRectangle(level, pyscreen)

        topRect = pygame.Rect(playRect.topleft, (playRect.width, tileSize))
        leftRect = pygame.Rect(playRect.topleft, (tileSize, playRect.height))
        rightRect = pygame.Rect((playRect.topright[0] - tileSize, playRect.topright[1]), (tileSize, playRect.height))
        bottomRect = pygame.Rect((playRect.bottomleft[0], playRect.bottomleft[1] - tileSize), (playRect.width, tileSize))

        pygame.draw.rect(pyscreen, borderColor, topRect, 0)
        pygame.draw.rect(pyscreen, borderColor, leftRect, 0)
        pygame.draw.rect(pyscreen, borderColor, rightRect, 0)
        pygame.draw.rect(pyscreen, borderColor, bottomRect, 0)

    def drawPlayer(self, app: App, pyscreen, now):
        level = app.session.level

        if level.isPlayerDead:
            text = self.__scoreFont.render("RIP", True, app.engine.style.playerDeadColor)

            textRect = text.get_rect()
            textRect.center = pyscreen.get_rect().center

            pyscreen.blit(text, textRect)

            timeSinceLastDeadSegment = now - self.__lastDeadSectionAdded
            if timeSinceLastDeadSegment >= 100:
                self.__lastDeadSectionAdded = now
                self.__playerDeadSections += 1

        timeSinceLastAte = now - level.playerLastTimeAte

        playerSegmentCount = len(level.playerLocations)
        for index, playerLocation in enumerate(reversed(level.playerLocations)):
            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            fillColor = None

            if level.isPlayerDead:
                if index >= playerSegmentCount - self.__playerDeadSections:
                    fillColor = app.engine.style.playerDeadColor
                else:
                    fillColor = app.engine.style.playerBodyColor
            elif isHeadSection:
                fillColor = app.engine.style.playerHeadColor
            else:
                fillColor = app.engine.style.playerBodyColor

            drawLocation = pygame.Rect(self.getLocationRect(level, pyscreen, playerLocation))

            if not isHeadSection:
                drawLocation.inflate_ip(-2, -2)

            if realIndex == 0:
                animationSegment1RunTime = 100
                animationSegment2RunTime = 100

                animationRunTime = animationSegment1RunTime + animationSegment2RunTime

                animationStartTime = level.playerLastTimeAte
                animationEndTime = animationStartTime + animationRunTime

                if now >= animationStartTime and now <= animationEndTime:
                    animationSegment1StartTime = animationStartTime
                    animationSegment2StartTime = animationSegment1StartTime + animationSegment1RunTime

                    increase = 0

                    if now >= animationSegment1StartTime and now < animationSegment2StartTime:
                        # Animation Section 1
                        increaseRatio = 3 / animationSegment1RunTime
                        increase = (now - animationStartTime) * increaseRatio
                    elif now >= animationSegment2StartTime and now < animationEndTime:
                        # Animation Section 2
                        increaseRatio = 2.5 / animationSegment2RunTime
                        increase = (animationStartTime - now) * increaseRatio

                    drawLocation.inflate_ip(increase, increase)

            if level.isPlayerDead:
                timeSinceDead = now - level.playerDeathTime
                increaseRatio = 4 / 200
                increase = timeSinceDead * increaseRatio

                drawLocation.inflate_ip(increase, increase)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

            if app.debug.playerLocation:
                string = f"{playerLocation[0]}, {playerLocation[1]}"
                text = self.__debugFont.render(string, True, (255, 0, 0), (255, 255, 255))

                textRect = text.get_rect()
                textRect.topleft = (drawLocation[0], drawLocation[1])

                pyscreen.blit(text, textRect)

    def drawFood(self, app: App, pyscreen):
        level = app.session.level

        drawLocation = self.getLocationRect(level, pyscreen, level.foodLocation)

        drawRect = pygame.Rect(drawLocation)

        drawRect = drawRect.inflate(-8, -8)

        pygame.draw.rect(pyscreen, app.engine.style.foodColor, drawRect, 0)

    def drawScore(self, app: App, pyscreen):
        level = app.session.level

        screenrect = pyscreen.get_rect()
        playRectangle = self.getPlayRectangle(level, pyscreen)

        rightSideBarWidth = screenrect.right - playRectangle.right

        scoreHeaderText = self.__scoreFont.render(str("Score"), True, app.engine.style.inGameScoreTextColor)
        scoreHeaderTextLocation = scoreHeaderText.get_rect()

        scoreHeaderLocation = pygame.Rect(playRectangle.right, playRectangle.top, rightSideBarWidth, scoreHeaderTextLocation.height)

        pygame.draw.rect(pyscreen, app.engine.style.inGameScoreHeaderBackgroundColor, scoreHeaderLocation)

        scoreHeaderTextLocation.midright = scoreHeaderLocation.midright
        scoreHeaderTextLocation.x -= 5

        pyscreen.blit(scoreHeaderText, scoreHeaderTextLocation)

        scoreText = self.__scoreFont.render(str(level.score), True, app.engine.style.inGameScoreTextColor)

        scoreTextLocation = scoreText.get_rect()
        scoreTextLocation.topright = scoreHeaderTextLocation.bottomright

        pyscreen.blit(scoreText, scoreTextLocation)

        string = f"{level.playerSpeed} + {level.playerSpeedBoost:0.2f} t/s"
        text = self.__statsFont.render(string, True, app.engine.style.inGameStatsTextColor)

        textRect = text.get_rect()
        textRect.topright = scoreTextLocation.bottomright

        textRect.top += 5

        pyscreen.blit(text, textRect)

    def getTileSize(self, level: Level, pyscreen):
        size = pyscreen.get_size()

        # padding
        size = (size[0] - 10, size[1] - 10)

        tileWidth = size[0] / level.width
        tileHeight = size[1] / level.height

        tileWidth = int(tileWidth)
        tileHeight = int(tileHeight)

        return min(tileWidth, tileHeight)

    def getPlayRectangle(self, level: Level, pyscreen):
        tileSize = self.getTileSize(level, pyscreen)

        rect = pygame.Rect(0, 0, level.width * tileSize, level.height * tileSize)

        rect.center = pyscreen.get_rect().center

        return rect
    
    def getLocationRect(self, level: Level, pyscreen, location):
        playRect = self.getPlayRectangle(level, pyscreen)
        tileSize = self.getTileSize(level, pyscreen)

        x = (location[0] * tileSize) + playRect.x
        y = (location[1] * tileSize) + playRect.y

        return (x, y, tileSize, tileSize)
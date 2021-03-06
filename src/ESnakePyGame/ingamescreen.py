import pygame
import logging
from ESnake import Direction, AppScreen, App, Level

class PyInGameScreenEngine:
    def __init__(self, app: App, level: Level):
        self.logger = logging.getLogger(__name__)
        self.__debugFont = pygame.font.SysFont("Lucida Console", 8)
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
                self.logger.debug("Requested Direction changed to Left");
                self.__level.player.requestedDirection = Direction.left
            elif event.key == pygame.K_RIGHT:
                self.logger.debug("Requested Direction changed to Right");
                self.__level.player.requestedDirection = Direction.right
            elif event.key == pygame.K_UP:
                self.logger.debug("Requested Direction changed to Up");
                self.__level.player.requestedDirection = Direction.up
            elif event.key == pygame.K_DOWN:
                self.logger.debug("Requested Direction changed to Down");
                self.__level.player.requestedDirection = Direction.down
            elif event.key == pygame.K_ESCAPE:
                self.logger.debug("esc pressed, switch to post game");
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
        self.drawBots(app, pyscreen, now)
        self.drawScore(app, pyscreen)
        
    def drawBorder(self, app, pyscreen):
        borderColor = app.engine.style.inGameWallColor

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
        if self.__level.player.isDead:
            text = self.__scoreFont.render("RIP", True, app.engine.style.playerDeadColor)

            textRect = text.get_rect()
            textRect.center = pyscreen.get_rect().center

            pyscreen.blit(text, textRect)

            timeSinceLastDeadSegment = now - self.__lastDeadSectionAdded
            if timeSinceLastDeadSegment >= 100:
                self.__lastDeadSectionAdded = now
                self.__playerDeadSections += 1

        timeSinceLastAte = now - self.__level.player.lastTimeAte

        playerSegmentCount = len(self.__level.player.segments)
        for index, segment in enumerate(reversed(self.__level.player.segments)):
            playerLocation = segment.location

            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, playerLocation))

            msPerTile = self.__level.player.speed

            timeSinceLastMove = now - self.__level.player.lastTimeMoved + self.__level.timeOffset

            percentToMove = min(1, timeSinceLastMove / msPerTile)

            if segment.direction == Direction.left:
                xOffset = drawLocation.width * percentToMove
                drawLocation[0] -= xOffset
            elif segment.direction == Direction.right:
                xOffset = drawLocation.width * percentToMove
                drawLocation[0] += xOffset
            elif segment.direction == Direction.up:
                yOffset = drawLocation.height * percentToMove
                drawLocation[1] -= yOffset
            elif segment.direction == Direction.down:
                yOffset = drawLocation.height * percentToMove
                drawLocation[1] += yOffset

            fillColor = None

            if self.__level.player.isDead:
                if index >= playerSegmentCount - self.__playerDeadSections:
                    fillColor = app.engine.style.playerDeadColor
                else:
                    fillColor = app.engine.style.playerBodyColor
            elif isHeadSection:
                fillColor = app.engine.style.playerHeadColor
                player = self.__level.player
                if player.previousRequestedDirection != player.direction:
                    fillColor = (184, 92, 0)
                    if player.direction == Direction.left or player.direction == Direction.right:
                        drawLocation.inflate_ip(-5, 0)
                    elif player.direction == Direction.up or player.direction == Direction.down:
                        drawLocation.inflate_ip(0, -5)
            else:
                fillColor = app.engine.style.playerBodyColor 

            if not isHeadSection:
                drawLocation.inflate_ip(-4, -4)

            if realIndex == 0:
                animationSegment1RunTime = 100
                animationSegment2RunTime = 100

                animationRunTime = animationSegment1RunTime + animationSegment2RunTime

                animationStartTime = self.__level.player.lastTimeAte
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

            if self.__level.player.isDead:
                timeSinceDead = now - self.__level.player.deathTime
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

    def drawBots(self, app, pyscreen, now):
        for bot in self.__level.bots:
            self.drawBot(app, pyscreen, now, bot)

    def drawBot(self, app, pyscreen, now, bot):
        if bot.isDead:
            # draw bot score
            string = f"{bot.score}"
            text = self.__debugFont.render(string, True, (255, 0, 0), (50, 0, 0))

            drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, bot.segments[0].location))

            textRect = text.get_rect()
            textRect.topleft = (drawLocation[0], drawLocation[1])

            pyscreen.blit(text, textRect)
            return

        timeSinceLastAte = now - bot.lastTimeAte

        playerSegmentCount = len(bot.segments)
        for index, segment in enumerate(reversed(bot.segments)):
            playerLocation = segment.location
            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, playerLocation))

            fillColor = None

            if isHeadSection:
                fillColor = app.engine.style.botHeadColor
                if bot.previousRequestedDirection != bot.direction:
                    fillColor = (184, 92, 0)
                    if bot.direction == Direction.left or bot.direction == Direction.right:
                        drawLocation.inflate_ip(-5, 0)
                    elif bot.direction == Direction.up or bot.direction == Direction.down:
                        drawLocation.inflate_ip(0, -5)
            else:
                fillColor = app.engine.style.botBodyColor

            if not isHeadSection:
                drawLocation.inflate_ip(-4, -4)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

        # draw energy bar
        fillColor = app.engine.style.playerEnergyBarColor
        drawLocation[3] = drawLocation[3] * 0.10
        drawLocation[2] = drawLocation[2] * bot.energy # energy is a number between 0 and 1
        pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)


    def drawFood(self, app, pyscreen):
        for food in self.__level.foods:
            drawLocation = self.getLocationRect(app, pyscreen, food.location)

            drawRect = pygame.Rect(drawLocation)

            drawRect = drawRect.inflate(-8, -8)

            pygame.draw.rect(pyscreen, app.engine.style.foodColor, drawRect, 0)

    def drawScore(self, app, pyscreen):
        screenrect = pyscreen.get_rect()
        playRectangle = self.getPlayRectangle(pyscreen)

        rightSideBarWidth = screenrect.right - playRectangle.right

        scoreHeaderText = self.__scoreFont.render(str("Score"), True, app.engine.style.inGameScoreTextColor)
        scoreHeaderTextLocation = scoreHeaderText.get_rect()

        scoreHeaderLocation = pygame.Rect(playRectangle.right, playRectangle.top, rightSideBarWidth, scoreHeaderTextLocation.height)

        pygame.draw.rect(pyscreen, app.engine.style.inGameScoreHeaderBackgroundColor, scoreHeaderLocation)

        scoreHeaderTextLocation.midright = scoreHeaderLocation.midright
        scoreHeaderTextLocation.x -= 5

        pyscreen.blit(scoreHeaderText, scoreHeaderTextLocation)

        scoreText = self.__scoreFont.render(str(self.__level.player.score), True, app.engine.style.inGameScoreTextColor)

        scoreTextLocation = scoreText.get_rect()
        scoreTextLocation.topright = scoreHeaderTextLocation.bottomright

        pyscreen.blit(scoreText, scoreTextLocation)

        bestBotScore = 0
        if self.__level.bestBot != None:
            bestBotScore = int(self.__level.bestBot.score)
        botscoreText = self.__scoreFont.render(str(bestBotScore), True, app.engine.style.inGameScoreTextColor)

        botscoreTextLocation = botscoreText.get_rect()
        botscoreTextLocation.topright = scoreTextLocation.bottomright

        pyscreen.blit(botscoreText, botscoreTextLocation)

        string = f"{self.__level.player.speed} + {self.__level.player.speedBoost:0.2f} t/s"
        text = self.__statsFont.render(string, True, app.engine.style.inGameStatsTextColor)

        textRect = text.get_rect()
        textRect.topright = botscoreTextLocation.bottomright

        textRect.top += 5

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
import pygame
import logging
from ESnake.direction import Direction
from ESnake.level import Level
from ESnakePyGame.screen import Screen
from ESnakePyGame.engine import PyGameEngine

class PyInGameScreenEngine:
    def __init__(self, engine: PyGameEngine):
        if engine == None: raise Exception("engine can't be None")

        self._log = logging.getLogger(__name__)
        self._engine: PyGameEngine = engine
        self.__debugFont = pygame.font.SysFont("Lucida Console", 14)
        self.__scoreFont = pygame.font.Font(engine.style.inGameScoreFont, engine.style.inGameScoreFontSize)
        self.__statsFont = pygame.font.Font(engine.style.inGameStatsFont, engine.style.inGameStatsFontSize)
        self.__playerDeadSections: int = 0
        self.__lastDeadSectionAdded: int = 0

    @property
    def level(self) -> Level: return self._engine.session.level

    def start(self, time: int):
        self.level.player.spawn(time)

    def processEvent(self, event):
        time = pygame.time.get_ticks()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._log.debug("Requested Direction changed to Left");
                if self.level.player.state == "spawned": self.level.player.start(time)
                self.level.player.nextDirection = Direction.left
            elif event.key == pygame.K_RIGHT:
                self._log.debug("Requested Direction changed to Right");
                if self.level.player.state == "spawned": self.level.player.start(time)
                self.level.player.nextDirection = Direction.right
            elif event.key == pygame.K_UP:
                self._log.debug("Requested Direction changed to Up");
                if self.level.player.state == "spawned": self.level.player.start(time)
                self.level.player.nextDirection = Direction.up
            elif event.key == pygame.K_DOWN:
                self._log.debug("Requested Direction changed to Down");
                if self.level.player.state == "spawned": self.level.player.start(time)
                self.level.player.nextDirection = Direction.down
            elif event.key == pygame.K_ESCAPE:
                self._log.debug("esc pressed, switch to post game");
                self._engine.screen = Screen.PostGame
    
    def update(self, time: int):
        self.level.update(time)

        if not self.level.player.state == "dead":
            self.level.player.update(time)
        else:
            msSincePlayerDied = time - self.level.player.deathTime

            if msSincePlayerDied >= 3000:
                self._log.debug("done with death delay")
                self._engine.screen = Screen.PostGame

    def draw(self, pyscreen, time: int):
        pyscreen.fill(self._engine.style.gameBackgroundColor)

        self.drawBorder(pyscreen)
        self.drawFood(pyscreen)
        self.drawPlayer(pyscreen, time)
        self.drawScore(pyscreen)
        
    def drawBorder(self, pyscreen):
        borderColor = self._engine.style.inGameWallColor

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

    def drawPlayer(self, pyscreen, time: int):
        if self.level.player.state == "dead":
            text = self.__scoreFont.render("RIP", True, self._engine.style.playerDeadColor)

            textRect = text.get_rect()
            textRect.center = pyscreen.get_rect().center

            pyscreen.blit(text, textRect)

            timeSinceLastDeadSegment = time - self.__lastDeadSectionAdded
            if timeSinceLastDeadSegment >= 100:
                self.__lastDeadSectionAdded = time
                self.__playerDeadSections += 1

        timeSinceLastAte = time - self.level.player.lastEatTime

        playerSegmentCount = len(self.level.player.segments)
        for index, playerLocation in enumerate(reversed(self.level.player.segments)):
            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            fillColor = None

            if self.level.player.state == "dead":
                if index >= playerSegmentCount - self.__playerDeadSections:
                    fillColor = self._engine.style.playerDeadColor
                else:
                    fillColor = self._engine.style.playerBodyColor
            elif isHeadSection:
                fillColor = self._engine.style.playerHeadColor
            else:
                fillColor = self._engine.style.playerBodyColor

            drawLocation = pygame.Rect(self.getLocationRect(pyscreen, playerLocation))

            if not isHeadSection:
                drawLocation.inflate_ip(-2, -2)

            if realIndex == 0:
                animationSegment1RunTime = 100
                animationSegment2RunTime = 100

                animationRunTime = animationSegment1RunTime + animationSegment2RunTime

                animationStartTime = self.level.player.lastEatTime
                animationEndTime = animationStartTime + animationRunTime

                if time >= animationStartTime and time <= animationEndTime:
                    animationSegment1StartTime = animationStartTime
                    animationSegment2StartTime = animationSegment1StartTime + animationSegment1RunTime

                    increase = 0

                    if time >= animationSegment1StartTime and time < animationSegment2StartTime:
                        # Animation Section 1
                        increaseRatio = 3 / animationSegment1RunTime
                        increase = (time - animationStartTime) * increaseRatio
                    elif time >= animationSegment2StartTime and time < animationEndTime:
                        # Animation Section 2
                        increaseRatio = 2.5 / animationSegment2RunTime
                        increase = (animationStartTime - time) * increaseRatio

                    drawLocation.inflate_ip(increase, increase)

            if self.level.player.state == "dead":
                timeSinceDead = time - self.level.player.deathTime
                increaseRatio = 4 / 200
                increase = timeSinceDead * increaseRatio

                drawLocation.inflate_ip(increase, increase)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

            if self._engine.config.debug.playerLocation:
                string = f"{playerLocation.x}, {playerLocation.y}"
                text = self.__debugFont.render(string, True, (255, 0, 0), (255, 255, 255))

                textRect = text.get_rect()
                textRect.topleft = (drawLocation[0], drawLocation[1])

                pyscreen.blit(text, textRect)

    def drawFood(self, pyscreen):
        drawLocation = self.getLocationRect(pyscreen, self.level.foodLocation)

        drawRect = pygame.Rect(drawLocation)

        drawRect = drawRect.inflate(-8, -8)

        pygame.draw.rect(pyscreen, self._engine.style.foodColor, drawRect, 0)

    def drawScore(self, pyscreen):
        screenrect = pyscreen.get_rect()
        playRectangle = self.getPlayRectangle(pyscreen)

        rightSideBarWidth = screenrect.right - playRectangle.right

        scoreHeaderText = self.__scoreFont.render(str("Score"), True, self._engine.style.inGameScoreTextColor)
        scoreHeaderTextLocation = scoreHeaderText.get_rect()

        scoreHeaderLocation = pygame.Rect(playRectangle.right, playRectangle.top, rightSideBarWidth, scoreHeaderTextLocation.height)

        pygame.draw.rect(pyscreen, self._engine.style.inGameScoreHeaderBackgroundColor, scoreHeaderLocation)

        scoreHeaderTextLocation.midright = scoreHeaderLocation.midright
        scoreHeaderTextLocation.x -= 5

        pyscreen.blit(scoreHeaderText, scoreHeaderTextLocation)

        scoreText = self.__scoreFont.render(str(self.level.player.score), True, self._engine.style.inGameScoreTextColor)

        scoreTextLocation = scoreText.get_rect()
        scoreTextLocation.topright = scoreHeaderTextLocation.bottomright

        pyscreen.blit(scoreText, scoreTextLocation)

        string = f"{self.level.player.speed} + {self.level.player.speedBoost:0.2f} t/s"
        text = self.__statsFont.render(string, True, self._engine.style.inGameStatsTextColor)

        textRect = text.get_rect()
        textRect.topright = scoreTextLocation.bottomright

        textRect.top += 5

        pyscreen.blit(text, textRect)

    def getTileSize(self, pyscreen):
        size = pyscreen.get_size()

        # padding
        size = (size[0] - 10, size[1] - 10)

        tileWidth = size[0] / self.level.width
        tileHeight = size[1] / self.level.height

        tileWidth = int(tileWidth)
        tileHeight = int(tileHeight)

        return min(tileWidth, tileHeight)

    def getPlayRectangle(self, pyscreen):
        tileSize = self.getTileSize(pyscreen)

        rect = pygame.Rect(0, 0, self.level.width * tileSize, self.level.height * tileSize)

        rect.center = pyscreen.get_rect().center

        return rect
    
    def getLocationRect(self, pyscreen, location):
        playRect = self.getPlayRectangle(pyscreen)
        tileSize = self.getTileSize(pyscreen)

        x = (location.x * tileSize) + playRect.x
        y = (location.y * tileSize) + playRect.y

        return (x, y, tileSize, tileSize)
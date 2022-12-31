import pygame
import logging
from ESnake import Direction, AppScreen, App, Level, Food, Snake, Wall


class PyInGameScreenEngine:
    def __init__(self, app: App, level: Level):
        self.logger = logging.getLogger(__name__)
        self.__debugFont = pygame.font.SysFont("Lucida Console", 8)
        self.__scoreFont = pygame.font.Font(
            app.engine.style.inGameScoreFont, app.engine.style.inGameScoreFontSize)
        self.__statsFont = pygame.font.Font(
            app.engine.style.inGameStatsFont, app.engine.style.inGameStatsFontSize)
        # TODO: Make this self.level
        self.__level: Level = level
        self.__playerDeadSections: int = 0
        self.__lastDeadSectionAdded: int = 0

    @property
    def level(self): return self.__level

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.logger.debug("Requested Direction changed to Left")
                self.__level.player.requestedDirection = Direction.left()
            elif event.key == pygame.K_RIGHT:
                self.logger.debug("Requested Direction changed to Right")
                self.__level.player.requestedDirection = Direction.right()
            elif event.key == pygame.K_ESCAPE:
                self.logger.debug("esc pressed, switch to post game")
                app.screen = AppScreen.PostGame
            elif event.key == pygame.K_LEFTBRACKET:
                if not hasattr(self.__level, 'maxBotCount'):
                    setattr(self.__level, 'maxBotCount',
                            self.__level.initialBotCount)
                self.__level.maxBotCount = max(1, self.__level.maxBotCount - 1)
                self.logger.debug("Reduced bot count to " +
                                  str(self.__level.maxBotCount))
            elif event.key == pygame.K_RIGHTBRACKET:
                if not hasattr(self.__level, 'maxBotCount'):
                    setattr(self.__level, 'maxBotCount',
                            self.__level.initialBotCount)
                self.__level.maxBotCount = min(
                    1000, self.__level.maxBotCount + 1)
                self.logger.debug("Increased bot count to " +
                                  str(self.__level.maxBotCount))
            elif event.key == pygame.K_r:
                self.logger.debug("Requested to respawn best bot")
                self.__level.respawnBest()

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
        rightRect = pygame.Rect(
            (playRect.topright[0] - tileSize, playRect.topright[1]), (tileSize, playRect.height))
        bottomRect = pygame.Rect(
            (playRect.bottomleft[0], playRect.bottomleft[1] - tileSize), (playRect.width, tileSize))

        pygame.draw.rect(pyscreen, borderColor, topRect, 0)
        pygame.draw.rect(pyscreen, borderColor, leftRect, 0)
        pygame.draw.rect(pyscreen, borderColor, rightRect, 0)
        pygame.draw.rect(pyscreen, borderColor, bottomRect, 0)

    def drawPlayer(self, app, pyscreen, now):
        if self.__level.player.isDead:
            text = self.__scoreFont.render(
                "RIP", True, app.engine.style.playerDeadColor)

            textRect = text.get_rect()
            textRect.center = pyscreen.get_rect().center

            pyscreen.blit(text, textRect)

            timeSinceLastDeadSegment = now - self.__lastDeadSectionAdded
            if timeSinceLastDeadSegment >= 100:
                self.__lastDeadSectionAdded = now
                self.__playerDeadSections += 1

        playerSegmentCount = len(self.__level.player.segments)
        for index, segment in enumerate(reversed(self.__level.player.segments)):
            playerLocation = segment.location

            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            drawLocation = pygame.Rect(
                self.getLocationRect(app, pyscreen, playerLocation))

            fillColor = None

            if isHeadSection:
                fillColor = app.engine.style.playerHeadColor
            else:
                fillColor = app.engine.style.playerBodyColor

            if not isHeadSection:
                drawLocation.inflate_ip(-4, -4)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

            if app.debug.playerLocation:
                string = f"{playerLocation[0]}, {playerLocation[1]}"
                text = self.__debugFont.render(
                    string, True, (255, 0, 0), (255, 255, 255))

                textRect = text.get_rect()
                textRect.topleft = (drawLocation[0], drawLocation[1])

                pyscreen.blit(text, textRect)

    def drawBots(self, app, pyscreen, now):
        for bot in self.__level.bots:
            self.drawBot(app, pyscreen, now, bot)

    def drawBot(self, app, pyscreen, now, bot):
        if bot.isDead:
            # draw bot score
            if bot.score > 3:
                string = f"{bot.score}"
                text = self.__debugFont.render(
                    string, True, (255, 0, 0), (50, 0, 0))

                drawLocation = pygame.Rect(self.getLocationRect(
                    app, pyscreen, bot.segments[0].location))

                textRect = text.get_rect()
                textRect.topleft = (drawLocation[0], drawLocation[1])

                pyscreen.blit(text, textRect)
            return

        bot_color = bot.controller.color

        playerSegmentCount = len(bot.segments)
        for index, segment in enumerate(reversed(bot.segments)):
            index_percent = max(0.5, index / playerSegmentCount)
            playerLocation = segment.location
            realIndex = (playerSegmentCount - index - 1)

            isHeadSection = index == playerSegmentCount - 1

            drawLocation = pygame.Rect(
                self.getLocationRect(app, pyscreen, playerLocation))

            fillColor = None

            if isHeadSection:
                fillColor = bot_color
                
                fillColor = (fillColor[0] * bot.energy, fillColor[1] * bot.energy, fillColor[2] * bot.energy)
            else:
                fillColor = bot_color
                fillColor = (fillColor[0] * index_percent, fillColor[1] * index_percent, fillColor[2] * index_percent)

            if not isHeadSection:
                drawLocation.inflate_ip(-4, -4)

            pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

        # draw energy bar
        fillColor = app.engine.style.playerEnergyBarColor
        drawLocation[3] = drawLocation[3] * 0.10
        # energy is a number between 0 and 1
        drawLocation[2] = drawLocation[2] * bot.energy
        pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

        # draw bot view locations, using green circles
        if app.debug.botViewLocations:
            if bot.viewLocations is not None:
                # different color for each location
                for index, location in enumerate(bot.viewLocations):
                    drawLocation = pygame.Rect(
                        self.getLocationRect(app, pyscreen, location))
                    drawLocation.inflate_ip(-4, -4)

                    contents = bot.viewContents[index]

                    color = (255, 255, 255)

                    if contents is None:
                        # nothing, probably outside of bounds
                        # dark grey
                        color = (100, 100, 100)
                    elif contents is bot:
                        # self
                        # cyan
                        color = (0, 255, 255)
                    elif isinstance(contents, Food):
                        # Food to eat
                        # green
                        color = (0, 255, 0)
                    elif isinstance(contents, Snake):
                        # other ai snek
                        # red
                        color = (255, 0, 0)
                    elif contents is self.level.player:
                        # other snek, player snek
                        # orange red
                        color = (255, 69, 0)
                    elif isinstance(contents, Wall):
                        # wall
                        # pink
                        color = (255, 0, 255)
                    else:
                        raise "invalid contents"                    

                    pygame.draw.circle(pyscreen, color, drawLocation.center, 2)
        
            # if the bot was created within the last 2 seconds, draw a little white circle in the middle of it
            adj_time = self.level.timeOffset + now
            bst = bot.startTime
            if bst is None:
                bst = adj_time
            if adj_time - bst < 2000:
                drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, bot.segments[0].location))
                drawLocation.inflate_ip(-2, -2)
                pygame.draw.circle(pyscreen, (255, 255, 255), drawLocation.center, 2)

            # draw little triangle on bot head pointing in direction of movement
            #drawLocation = pygame.Rect(
            #    self.getLocationRect(app, pyscreen, bot.segments[0].location))
            #drawLocation.inflate_ip(-4, -4)
#
            #center = drawLocation.center
            #width = drawLocation.width
            #height = drawLocation.height
#
            #if bot.direction == Direction.up():
            #    points = [
            #        (center[0], center[1] - height / 2),
            #        (center[0] - width / 2, center[1] + height / 2),
            #        (center[0] + width / 2, center[1] + height / 2)
            #    ]
            #elif bot.direction == Direction.down():
            #    points = [
            #        (center[0], center[1] + height / 2),
            #        (center[0] - width / 2, center[1] - height / 2),
            #        (center[0] + width / 2, center[1] - height / 2)
            #    ]
            #elif bot.direction == Direction.left():
            #    points = [
            #        (center[0] - width / 2, center[1]),
            #        (center[0] + width / 2, center[1] - height / 2),
            #        (center[0] + width / 2, center[1] + height / 2)
            #    ]
            #elif bot.direction == Direction.right():
            #    points = [
            #        (center[0] + width / 2, center[1]),
            #        (center[0] - width / 2, center[1] - height / 2),
            #        (center[0] - width / 2, center[1] + height / 2)
            #    ]
#
            #pygame.draw.polygon(pyscreen, (255, 0, 0), points)

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

        scoreHeaderLocation = pygame.Rect(
            playRectangle.right, playRectangle.top, rightSideBarWidth, scoreHeaderTextLocation.height)

        pygame.draw.rect(pyscreen, app.engine.style.inGameScoreHeaderBackgroundColor, scoreHeaderLocation)

        scoreHeaderTextLocation.midleft = scoreHeaderLocation.midleft
        scoreHeaderTextLocation.x += 2

        pyscreen.blit(scoreHeaderText, scoreHeaderTextLocation)

        scoreText = self.__scoreFont.render(
            str(self.__level.player.score), True, app.engine.style.inGameScoreTextColor)

        scoreTextLocation = scoreText.get_rect()
        scoreTextLocation.topleft = scoreHeaderTextLocation.bottomleft

        pyscreen.blit(scoreText, scoreTextLocation)

        # Draw all best bot scores.
        # The scores should start on the left side of the right side bar, and be listed vertically.
        # Each entry should have a square with the bot controller color on the left and the score to the right of it.
        # we can only stack about MAX_BOT_ROWS entries per column, so we need to make multiple columns if there are more than MAX_BOT_ROWS entries.
        MAX_BOT_ROWS = 40
        botscoreTextLocation = scoreTextLocation
        last_column_location = None
        for index, bot in enumerate(self.__level.bestBots):
            # Draw the bot color square
            bot_color = bot.controller.color
            bot_color_rect = pygame.Rect(botscoreTextLocation.left, botscoreTextLocation.top + 22, 20, 20)

            if index % MAX_BOT_ROWS == 0:
                # we need to start a new column
                if last_column_location is None:
                    # this is the first column
                    last_column_location = bot_color_rect
                else:
                    # this is not the first column
                    last_column_location = last_column_location.move(40, 0)
                    bot_color_rect.topleft = last_column_location.topleft

            pygame.draw.rect(pyscreen, bot_color, bot_color_rect, 0)

            # Draw the bot score
            botscoreText = self.__scoreFont.render(str(int(bot.score)), True, app.engine.style.inGameScoreTextColor)
            botscoreTextLocation = botscoreText.get_rect()
            botscoreTextLocation.topleft = bot_color_rect.topright
            pyscreen.blit(botscoreText, botscoreTextLocation)

            botscoreTextLocation = bot_color_rect

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

        rect = pygame.Rect(0, 0, self.__level.width *
                           tileSize, self.__level.height * tileSize)

        rect.center = pyscreen.get_rect().center

        return rect

    def getLocationRect(self, app, pyscreen, location):
        playRect = self.getPlayRectangle(pyscreen)
        tileSize = self.getTileSize(pyscreen)

        x = (location[0] * tileSize) + playRect.x
        y = (location[1] * tileSize) + playRect.y

        return (x, y, tileSize, tileSize)

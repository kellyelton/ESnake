import math
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
        self.__oldSegments: list = []

    @property
    def level(self): return self.__level

    def processEvent(self, app, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                cur_dir = self.__level.player.direction

                if cur_dir == Direction.left():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.right():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.up():
                    self.__level.player.requestedDirection = Direction.left()
                elif cur_dir == Direction.down():
                    self.__level.player.requestedDirection = Direction.right()
            elif event.key == pygame.K_RIGHT:
                cur_dir = self.__level.player.direction
                
                if cur_dir == Direction.left():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.right():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.up():
                    self.__level.player.requestedDirection = Direction.right()
                elif cur_dir == Direction.down():
                    self.__level.player.requestedDirection = Direction.left()
            elif event.key == pygame.K_UP:
                cur_dir = self.__level.player.direction
                
                if cur_dir == Direction.down():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.left():
                    self.__level.player.requestedDirection = Direction.right()
                elif cur_dir == Direction.right():
                    self.__level.player.requestedDirection = Direction.left()
                elif cur_dir == Direction.up():
                    self.__level.player.requestedDirection = Direction.none()
            elif event.key == pygame.K_DOWN:
                cur_dir = self.__level.player.direction
                
                if cur_dir == Direction.up():
                    self.__level.player.requestedDirection = Direction.none()
                elif cur_dir == Direction.left():
                    self.__level.player.requestedDirection = Direction.left()
                elif cur_dir == Direction.right():
                    self.__level.player.requestedDirection = Direction.right()
                elif cur_dir == Direction.up():
                    self.__level.player.requestedDirection = Direction.none()
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

        self.drawOldSegments(app, pyscreen)
        self.drawFood(app, pyscreen)
        self.drawPlayer(app, pyscreen, now)
        self.drawBots(app, pyscreen, now)
        self.drawScore(app, pyscreen)
        self.drawBorder(app, pyscreen)

    def drawBorder(self, app, pyscreen):
        borderColor = app.engine.style.inGameWallColor

        tileSize = self.getTileSize(pyscreen)

        playRect = self.getPlayRectangle(pyscreen)

        topRect = pygame.Rect(playRect.topleft, (playRect.width, tileSize))
        leftRect = pygame.Rect(playRect.topleft, (tileSize, playRect.height))
        rightRect = pygame.Rect(
            (playRect.right - tileSize, playRect.top), (tileSize, playRect.height))
        bottomRect = pygame.Rect(
            (playRect.left, playRect.bottom - tileSize), (playRect.width, tileSize))

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

        self.drawSnake(app, pyscreen, now, self.__level.player)

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
    
        self.drawSnake(app, pyscreen, now, bot)

    def drawSnake(self, app, pyscreen, now, snake):
        snake_color = snake.controller.color

        snakeSegmentCount = len(snake.segments)
        for index, segment in enumerate(reversed(snake.segments)):
            index_percent = max(0.05, index / snakeSegmentCount)
            snakeLocation = segment.location
            realIndex = (snakeSegmentCount - index - 1)

            isHeadSection = index == snakeSegmentCount - 1

            fillColor = None

            if isHeadSection:
                fillColor = snake_color
                fillColor = (fillColor[0] * snake.energy, fillColor[1] * snake.energy, fillColor[2] * snake.energy)

                self.__oldSegments.append((snakeLocation, fillColor, 0))

                drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, snakeLocation))
                drawLocation.inflate_ip(-10, -10)
                pygame.draw.circle(pyscreen, fillColor, drawLocation.center, drawLocation.width)
            else:
                fillColor = snake_color
                fillColor = (fillColor[0] * index_percent, fillColor[1] * index_percent, fillColor[2] * index_percent, snake.energy)

                # draw circle at playerLocation
                drawLocation = pygame.Rect(self.getLocationRect(app, pyscreen, snakeLocation))
                drawLocation.inflate_ip(-8, -8)
                size = int(( drawLocation.width) * index_percent)
                pygame.draw.circle(pyscreen, fillColor, drawLocation.center, size)

        # draw energy bar
        #fillColor = app.engine.style.playerEnergyBarColor
        #drawLocation[3] = drawLocation[3] * 0.10
        ## energy is a number between 0 and 1
        #drawLocation[2] = drawLocation[2] * bot.energy
        #pygame.draw.rect(pyscreen, fillColor, drawLocation, 0)

        if app.debug.botView2:
            # view2 = [[direction, distance, entity], ...]]
            if snake.view2 is not None:
                snake_location = snake.segments[0].location
                
                snake_direction = (snake.direction.x, snake.direction.y)

                # different color for each location
                for index, view in enumerate(snake.view2):
                    view_direction_radians = view[0]
                    distance = (((1 - view[1])) * (self.level.view2Distance)) * self.getTileSize(pyscreen)
                    reward = view[2]
                    punishment = view[3]

                    thickness = 1
                    color = (255, 255, 255)

                    if reward == 1:
                        # goodness
                        # green
                        color = (0, 255, 0)
                        thickness = 2
                    elif punishment == 1:
                        # death
                        # red
                        color = (255, 0, 0)
                        thickness = 2
                    else:
                        # unknown
                        # white
                        color = (snake_color[0] - 25, snake_color[1] - 25, snake_color[2] - 25)
                        thickness = 1

                    # find the endpoint
                    
                    # get the center of the bot
                    snakeRect = pygame.Rect(
                        self.getLocationRect(app, pyscreen, snake_location))
                    snakeRect.center = snakeRect.center

                    # correct the angle based on the bot's direction
                    view_direction_radians += math.atan2(
                        snake_direction[1], snake_direction[0])

                    # get the endpoint
                    endPoint = (
                        snakeRect.center[0] + (distance * math.cos(view_direction_radians)),
                        snakeRect.center[1] + (distance * math.sin(view_direction_radians))
                    )

                    pygame.draw.line(pyscreen, color, snakeRect.center, endPoint, thickness)

        if app.debug.botDirection and snake.viewLocations is not None:
            snake_location = snake.segments[0].location

            # draw a line from the bot to the direction
            # get the center of the bot
            snakeRect = pygame.Rect(
                self.getLocationRect(app, pyscreen, snake_location))
            snakeRect.center = snakeRect.center

            # get the angle
            angle = math.atan2(
                snake.direction.y, snake.direction.x)

            # get the end point
            endPoint = (
                snakeRect.center[0] + (snakeRect.width * math.cos(angle)),
                snakeRect.center[1] + (snakeRect.height * math.sin(angle))
            )

            pygame.draw.line(pyscreen, (255, 155, 255),
                             snakeRect.center, endPoint, 2)
        
    def drawOldSegments(self, app, pyscreen):
        for i, segment in enumerate(self.__oldSegments):
            drawLocation = segment[0]
            fillColor = segment[1]
            age = segment[2]

            # age is between 0 and 1, incrementing by 0.01 each frame
            age += 0.02

            self.__oldSegments[i] = (drawLocation, fillColor, age)

            if age >= 1:
                # remove the old segment
                self.__oldSegments.pop(i)
                continue
            
            color_scale = 10
            fillColor = (fillColor[0] * ((1 - age) / color_scale), fillColor[1] * ((1 - age) / color_scale), fillColor[2] * ((1 - age) / color_scale), age)

            drawLocation = self.getLocationRect(app, pyscreen, drawLocation)
            
            drawRect = pygame.Rect(drawLocation)
            #drawRect.inflate_ip(-10, -)
            drawRect.inflate_ip((20 * (age)) - 5, (20 * (age)) - 5)

            #pygame.draw.rect(pyscreen, fillColor, drawRect)
            pygame.draw.circle(pyscreen, fillColor, drawRect.center, drawRect.width)

    def drawFood(self, app, pyscreen):
        for food in self.__level.foods:
            drawLocation = self.getLocationRect(app, pyscreen, food.location)

            drawRect = pygame.Rect(drawLocation)

            drawBack = drawRect.inflate(-6, -6)
            drawRect = drawRect.inflate(-10, -10)
            
            pygame.draw.rect(pyscreen, (10, 10, 10), drawBack, 0)
            pygame.draw.rect(pyscreen, (45, 95, 45), drawRect, 0)

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

        rect.midleft = pyscreen.get_rect().midleft

        return rect

    def getLocationRect(self, app, pyscreen, location):
        playRect = self.getPlayRectangle(pyscreen)
        tileSize = self.getTileSize(pyscreen)

        x = (location[0] * tileSize) + playRect.x
        y = (location[1] * tileSize) + playRect.y

        return (x, y, tileSize, tileSize)

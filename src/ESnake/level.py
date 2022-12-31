import random
import logging
import numpy as np
import smtplib, ssl, json
import threading
import time
from random import randint
from . import updateHighScore, AppScreen, Snake, Food, Wall, GameObject
from .controllers import Dylan, Automatic


class Level:
    @staticmethod
    def default():
        return Level(60, 60, 5, 200, 30)

    def __init__(self, width, height, speed, foodCount, botCount):
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.foods = []
        self.player = None
        self.bots = []
        self.bestBots = []
        self.occupiedLocations = None
        self.timeOffset = 0
        self.initialFoodCount = foodCount
        self.initialBotCount = botCount
        self.maxBotCount = self.initialBotCount
        self.locations = [[None for x in range(width)] for y in range(height)]
        self.lastUpdateTime = 0

        for i in range(self.initialFoodCount):
            location = self.randomEmptyLocation
            food = Food(location)
            self.updateLocation(food)
            self.foods.append(food)

        self.player = Snake(speed, self.center, ["player"])
        self.updateLocation(self.player)

        self.bots = []
        for i in range(self.initialBotCount):
            location = self.randomEmptyLocation
            snake = Snake(speed, location, ["bot"], Dylan())
            self.updateLocation(snake)
            self.bots.append(snake)
        
        self.autobot = Snake(speed, self.randomEmptyLocation, ["bot", "auto"], Automatic())
        self.updateLocation(self.autobot)
        self.bots.append(self.autobot)

        self.startTime: int = None

    @property
    def center(self):
        return (self.width // 2, self.height // 2)

    @property
    def randomLocation(self):
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)

        return (x, y)

    @property
    def randomEmptyLocation(self):
        while True:
            # find empty random location
            location = self.randomLocation

            while not self.isEmpty(location):
                location = self.randomLocation
            
            # verify that there is nothing in the 4x4 grid around the location
            cx = location[0]
            cy = location[1]
            is_fully_empty = True
            for i in range(cx - 2, cx + 2):
                for j in range(cy - 2, cy + 2):
                    if not self.isEmpty((i, j)):
                        is_fully_empty = False
                        break
                if not is_fully_empty:
                    break

            if is_fully_empty:
                break

        return location

    def update(self, app, time):
        self.initialFoodCount = 20
        while len(self.foods) > self.initialFoodCount:
            self.foods.pop()
        time = time + self.timeOffset

        if self.startTime is None:
            self.startTime = time

        self.lastUpdateTime = time

        self.player.update(app, time, self)

        self.refreshOccupiedLocations()

        if self.player.isDead:
            msSincePlayerDied = time - self.player.deathTime

            if msSincePlayerDied >= 3000:
                self.logger.debug("done with death delay")
                app.screen = AppScreen.PostGame
                storedHighScore = updateHighScore(
                    app.config, self.player.score)
                if storedHighScore:
                    self.logger.debug("Got a high score")

        for bot in self.bots:
            bot.update(app, time, self)

            self.refreshOccupiedLocations()

            if bot.isDead:
                msSincePlayerDied = time - bot.deathTime

                if msSincePlayerDied >= 500:
                    self.logger.debug("done with death delay")

                    if bot.score > 1:
                        if len(self.bestBots) == 0:
                            self.bestBots.append(bot)
                        else:
                            for i in range(0, len(self.bestBots)):
                                if bot.score >= self.bestBots[i].score:
                                    self.bestBots.insert(i, bot)
                                    # bot name, aka, type of controller
                                    botName = bot.controller.__class__.__name__
                                    self.logger.info(
                                        f"Bot '{botName} entered {i + 1} place " +
                                        f"with score {bot.score}"
                                    )
                                    self.bestBots = self.bestBots[:160 * 2]

                                    if i == 0:
                                        self.sendHighScoreEmailInBackground(bot, time)

                                    break

                    self.bots.remove(bot)

                    self.refreshOccupiedLocations()

        if not hasattr(self, 'maxBotCount'):
            setattr(self, 'maxBotCount', self.initialBotCount)

        botLength = len(self.bots)

        if botLength < self.maxBotCount:
            diff = self.maxBotCount - botLength
            has_best_bots = len(self.bestBots) > 0

            # make sure that there's at least 1 best bot that's not an automatic bot
            if has_best_bots:
                for bot in self.bestBots:
                    if not isinstance(bot.controller, Automatic):
                        break
                else:
                    has_best_bots = False

            for i in range(0, diff):
                # if best bot count is 0, 100% chance to create a new bot
                # if best bot count is maxed at 100, 5% chance to create a new bot
                # reduce create new bot chance from 100% to 5% linearly as best bot count increases

                create_new_bot_chance = 1.0 - (0.95 * (len(self.bestBots) / 100))

                if not has_best_bots:
                    newController = Dylan()
                elif random.random() > create_new_bot_chance:
                    random_best = random.choice(self.bestBots)
                    while isinstance(random_best.controller, Automatic):
                        random_best = random.choice(self.bestBots)
                    newController = Dylan(random_best.controller)
                else:
                    newController = Dylan()

                newBot = Snake(bot.speed, self.randomEmptyLocation, ["bot"], newController)

                self.bots.append(newBot)

                self.refreshOccupiedLocations()
        
        # add autobot if it died and isn't int he bot list
        if self.autobot not in self.bots:
            # make new autobot
            self.autobot = Snake(self.autobot.speed, self.randomEmptyLocation, ["bot", "auto"], Automatic())
            self.updateLocation(self.autobot)
            self.bots.append(self.autobot)

            self.refreshOccupiedLocations()


    def respawnBest(self):
        if len(self.bestBots) == 0:
            return

        best = self.bestBots[0]

        newController = Dylan(best.controller, mutate=False)
        newbest = Snake(best.speed, self.randomEmptyLocation,
                        ["bot", "best"], newController)

        self.bots.append(newbest)
        self.refreshOccupiedLocations()

    def updateLocation(self, gameObject: GameObject):
        pass

    def refreshOccupiedLocations(self):
        if self.occupiedLocations is None:
            self.occupiedLocations = np.empty(
                shape=(self.height, self.width), dtype='object')
        else:
            self.occupiedLocations.fill(None)

        for food in self.foods:
            self.occupiedLocations[food.location[0]][food.location[1]] = food

        if self.player is not None:
            for segment in self.player.segments:
                self.occupiedLocations[segment.location[0]
                                       ][segment.location[1]] = self.player

        for bot in self.bots:
            for segment in bot.segments:
                self.occupiedLocations[segment.location[0]
                                       ][segment.location[1]] = bot

        for x in range(self.width):
            self.occupiedLocations[0][x] = Wall((x, 0))
            self.occupiedLocations[self.height -
                                   1][x] = Wall((x, self.height - 1))

        for y in range(self.height):
            self.occupiedLocations[y][0] = Wall((0, y))
            self.occupiedLocations[y][self.width -
                                      1] = Wall((self.width - 1, y))

    def getContents(self, location):
        if self.isOutsideWall(location):
            return None

        if self.occupiedLocations is None:
            if location[0] <= 0:
                return Wall(location)
            if location[0] >= self.width - 1:
                return Wall(location)

            if location[1] <= 0:
                return Wall(location)
            if location[1] >= self.height - 1:
                return Wall(location)

            for food in self.foods:
                if location == food.location:
                    return food

            if self.player is not None:
                for segment in self.player.segments:
                    if location == segment.location:
                        return self.player

            for bot in self.bots:
                for segment in bot.segments:
                    if location == segment.location:
                        return bot

            return None
        else:
            contents = self.occupiedLocations[location[0]][location[1]]

            return contents

    def isOutsideWall(self, location):
        if location[0] < 0:
            return True
        if location[0] > self.width - 1:
            return True

        if location[1] < 0:
            return True
        if location[1] > self.height - 1:
            return True

        return False

    def isEmpty(self, location):
        content = self.getContents(location)
        return content is None

    def moveFood(self, food):
        food.location = self.randomEmptyLocation
    
    def sendHighScoreEmailInBackground(self, bot: Snake, current_time):
        return
        thread = threading.Thread(target=self.sendHighScoreEmail, args=(bot, current_time,))
        thread.start()

    def sendHighScoreEmail(self, bot: Snake, current_time):
        # send me an email with the newest bot serialized to json

        botName = bot.controller.__class__.__name__

        # convert bot to json
        # exclude Logger
        botJson = ""
        
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender_email = ""
        receiver_email = ""

        message = MIMEMultipart("alternative")
        message["Subject"] = f'New Best Bot {botName} {bot.score}'
        message["From"] = sender_email
        message["To"] = receiver_email

        # runtime

        runtime = current_time - self.startTime
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(runtime))

        # Create the plain-text and HTML version of your message
        text = f"""\
        New Best Bot {botName} {bot.score}\n
        Time: {formatted_time}\
        """
        html = f"""\
        <html>
        <body>
            <p>New Best Bot {bot.score}</p>
            <p>Time: {formatted_time}</p>
            <p>{botJson}</p>
        </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("", "")
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

            server.quit()

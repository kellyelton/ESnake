import pygame
from ESnake.update import Updater
from ESnakePyGame.engine import PyGameEngine

class PyLoadingScreenEngine:
    def __init__(self, engine: PyGameEngine):
        self.__dotCount = 0
        self.__engine: PyGameEngine = engine
        self.__font = pygame.font.Font(engine.style.loadingScreenFont, engine.style.loadingScreenFontSize)
        self.__minorfont = pygame.font.Font(engine.style.loadingScreenFont, engine.style.loadingScreenFontSize - 10)
        self.__lastUpdateDotsTime = 0
        self.__loadingStartTime = 0
        self.__state = "initializing"
        self.__updater = Updater(engine.version, engine.exelocation)
        self.status = "Loading"
        self.minorstatus = ""

    def processEvent(self, event): pass
    def update(self, time: int): 
        if self.__state == "initializing":
            self.__state = "updating"
            self.__updater.start()
            self.status = self.__updater.status
            self.minorstatus = self.__updater.minorstatus
        elif self.__state == "updating":
            self.status = self.__updater.status
            self.minorstatus = self.__updater.minorstatus

            if self.__updater.isComplete:
                if self.__updater.shutdownForUpdate:
                    self.__engine.shutdown()
                    self.__state = "shutting down"
                    self.status = "Shutting Down"
                    self.minorstatus = ""
                else:
                    self.__state = "loading"
                    self.status = "Loading"
                    self.minorstatus = ""
                    self.__loadingStartTime = time
        elif self.__state == "loading":
            timeSinceLoadingStarted = time - self.__loadingStartTime

            if timeSinceLoadingStarted >= 1000:
                self.__engine.newGame()
        elif self.__state == "shutting down":
            pass
        else:
            raise Exception(f"Invalid state {self.__state}")

    def draw(self, pyscreen, time: int):
        msSinceLastDotUpdate = time - self.__lastUpdateDotsTime
        
        if msSinceLastDotUpdate > 500:
            self.__dotCount += 1
            if self.__dotCount == 4:
                self.__dotCount = 0

            self.__lastUpdateDotsTime = time

        pyscreen.fill(self.__engine.style.loadingBackgroundColor)

        pyscreenrect = pyscreen.get_rect()

        messagearearect = pyscreenrect.inflate(-(pyscreenrect.width / 5), -(pyscreenrect.height / 3))

        loadingDots = ""
        for _ in range(self.__dotCount):
            loadingDots += "."

        loadingString = self.status + loadingDots
        loadingStringLocation = messagearearect.topleft

        loadingStringRect = self.drawText(loadingString, loadingStringLocation, self.__font, self.__engine.style.loadingTextColor, pyscreen)

        minorStatusLocation = loadingStringRect.bottomleft
        minorStatusLocation = (minorStatusLocation[0], minorStatusLocation[1] + 10)

        self.drawText(self.minorstatus, minorStatusLocation, self.__minorfont, self.__engine.style.loadingTextColor, pyscreen)

    def drawText(self, message, location, font, color, pyscreen):
        text = font.render(message, True, color)

        textRect = text.get_rect()
        textRect.topleft = location

        pyscreen.blit(text, textRect)

        return textRect

import pygame
from ESnake import AppScreen, update

class PyLoadingScreenEngine:
    def __init__(self, app):
        self.__dotCount = 0
        self.__font = pygame.font.Font(app.engine.style.loadingScreenFont, app.engine.style.loadingScreenFontSize)
        self.__minorfont = pygame.font.Font(app.engine.style.loadingScreenFont, app.engine.style.loadingScreenFontSize - 10)
        self.__lastUpdateDotsTime = 0
        self.__loadingStartTime = 0
        self.__state = "initializing"
        self.__updater = update.Updater(app.version, app.exelocation)
        self.status = "Loading"
        self.minorstatus = ""

    def processEvent(self, app, event): pass
    def update(self, app): 
        now = pygame.time.get_ticks()

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
                    app.stop()
                    self.__state = "shutting down"
                    self.status = "Shutting Down"
                    self.minorstatus = ""
                else:
                    self.__state = "loading"
                    self.status = "Loading"
                    self.minorstatus = ""
                    self.__loadingStartTime = now
        elif self.__state == "loading":
            timeSinceLoadingStarted = now - self.__loadingStartTime

            if timeSinceLoadingStarted >= 1000:
                app.screen = AppScreen.InGame
        elif self.__state == "shutting down":
            pass
        else:
            raise Exception(f"Invalid state {self.__state}")

    def draw(self, app, pyscreen):
        now = pygame.time.get_ticks()

        msSinceLastDotUpdate = now - self.__lastUpdateDotsTime
        
        if msSinceLastDotUpdate > 500:
            self.__dotCount += 1
            if self.__dotCount == 4:
                self.__dotCount = 0

            self.__lastUpdateDotsTime = pygame.time.get_ticks()

        pyscreen.fill(app.engine.style.loadingBackgroundColor)

        pyscreenrect = pyscreen.get_rect()

        messagearearect = pyscreenrect.inflate(-(pyscreenrect.width / 5), -(pyscreenrect.height / 3))

        loadingDots = ""
        for _ in range(self.__dotCount):
            loadingDots += "."

        loadingString = self.status + loadingDots
        loadingStringLocation = messagearearect.topleft

        loadingStringRect = self.drawText(loadingString, loadingStringLocation, self.__font, app.engine.style.loadingTextColor, pyscreen)

        minorStatusLocation = loadingStringRect.bottomleft
        minorStatusLocation = (minorStatusLocation[0], minorStatusLocation[1] + 10)

        self.drawText(self.minorstatus, minorStatusLocation, self.__minorfont, app.engine.style.loadingTextColor, pyscreen)

    def drawText(self, message, location, font, color, pyscreen):
        text = font.render(message, True, color)

        textRect = text.get_rect()
        textRect.topleft = location

        pyscreen.blit(text, textRect)

        return textRect

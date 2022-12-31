import os
import sys

class Style:
    def __init__(self):
        mainBorderColor = (52, 10, 63)

        self.loadingBackgroundColor = (50, 0, 0)
        self.loadingTextColor = (200, 200, 200)
        self.loadingScreenFontSize = 46
        self.loadingScreenFont = self.getResourcePath("Fonts/Alata-Regular.ttf")
        self.loadingMinorTextColor = (150, 150, 150)
        self.loadingScreenMinorFontSize = 24
        self.loadingScreenMinorFont = self.getResourcePath("Fonts/Alata-Regular.ttf")

        self.gameBackgroundColor = (0, 0, 0)
        self.inGameWallColor = mainBorderColor
        self.inGameScoreTextColor = (255, 255, 255)
        self.inGameScoreFontSize = 14
        self.inGameScoreFont = self.getResourcePath("Fonts/Alata-Regular.ttf")
        self.inGameScoreHeaderBackgroundColor = mainBorderColor
        self.inGameStatsTextColor = (75, 75, 75)
        self.inGameStatsFontSize = 15
        self.inGameStatsFont = self.getResourcePath("Fonts/Alata-Regular.ttf")
        self.playerHeadColor = (108, 28, 206)
        self.playerEnergyBarColor = (200, 0, 0)
        self.playerBodyColor = (49, 13, 99)
        self.playerDeadColor = (138, 3, 3)
        self.botHeadColor = (28, 206, 108)
        self.botBodyColor = (9, 67, 35)
        self.foodColor = (150, 150, 150)

        self.postGameBackgroundColor = (50, 0, 0)
        self.postGameGameOverFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")
        self.postGameGameOverFontSize = 128
        self.postGameGameOverColor = (255, 53, 53)
        self.postGameScoreFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")
        self.postGameScoreFontSize = 64
        self.postGameScoreColor = (150, 150, 150)
        self.postGameInstructionsFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")
        self.postGameInstructionsFontSize = 32
        self.postGameInstructionsColor = (255, 128, 26)

    def getResourcePath(self, relativePath):
        if getattr(sys, 'frozen', False):
            rootDirectory = sys._MEIPASS
        else:
            rootDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        rootDirectory = os.path.join(rootDirectory, "Resources")

        path = os.path.join(rootDirectory, relativePath)

        return path

def loadStyle(styleName):
    if styleName.casefold() == 'classic'.casefold():
        return Style()
    else:
        raise Exception(f"Style '{styleName}' could not be found.")
import os

class ClassicStyle:
    def __init__(self):
        self.loadingBackgroundColor = (50, 0, 0)
        self.loadingTextColor = (200, 200, 200)
        self.loadingScreenFontSize = 64
        self.loadingScreenFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")

        self.gameBackgroundColor = (0, 0, 0)
        self.inGameScoreTextColor = (255, 255, 255)
        self.inGameScoreFontSize = 40
        self.inGameScoreFont = self.getResourcePath("Fonts/Alata-Regular.ttf")
        self.inGameStatsTextColor = (150, 255, 150)
        self.inGameStatsFontSize = 15
        self.inGameStatsFont = self.getResourcePath("Fonts/Alata-Regular.ttf")
        self.playerHeadColor = (145, 203, 255)
        self.playerBodyColor = (255, 255, 255)
        self.playerDeadColor = (138, 3, 3)
        self.foodColor = (50, 255, 50)

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
        rootDirectory = os.path.dirname(os.path.abspath(__file__))

        rootDirectory = os.path.join(rootDirectory, "Resources")

        path = os.path.join(rootDirectory, relativePath)

        return path
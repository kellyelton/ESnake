import os

class ClassicStyle:
    def __init__(self):
        self.gameBackgroundColor = (0, 0, 0)
        self.loadingBackgroundColor = (50, 0, 0)
        self.postGameBackgroundColor = (0, 0, 50)
        self.loadingTextColor = (200, 200, 200)
        self.loadingScreenFontSize = 64
        self.loadingScreenFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")
        self.inGameScoreTextColor = (200, 200, 200)
        self.inGameScoreFontSize = 32
        self.inGameScoreFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")
        self.playerColor = (255, 255, 255)
        self.foodColor = (50, 255, 50)

    def getResourcePath(self, relativePath):
        rootDirectory = os.path.dirname(os.path.abspath(__file__))

        rootDirectory = os.path.join(rootDirectory, "Resources")

        path = os.path.join(rootDirectory, relativePath)

        return path
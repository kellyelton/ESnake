import os

class ClassicStyle:
    def __init__(self):
        self.gameBackgroundColor = (0, 0, 0)
        self.loadingBackgroundColor = (50, 0, 0)
        self.postGameBackgroundColor = (0, 0, 50)
        self.loadingTextColor = (200, 200, 200)
        self.loadingScreenFontSize = 64
        self.loadingScreenFont = self.getResourcePath("Fonts/Amatic-Bold.ttf")

    def getResourcePath(self, relativePath):
        rootDirectory = os.path.dirname(os.path.abspath(__file__))

        rootDirectory = os.path.join(rootDirectory, "Resources")

        path = os.path.join(rootDirectory, relativePath)

        return path
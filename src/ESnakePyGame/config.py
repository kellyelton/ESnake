class Debug:
    def __init__(self):
        self.playerLocation = False

class Config:
    def __init__(self):
        self.style = "classic"
        self.maxfps = 60
        self.fullscreen = False
        self.screenSize = [800, 600]
        self.debug = Debug()
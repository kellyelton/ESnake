from .styles import ClassicStyle

class DefaultConfig:
    def __init__(self):
        self.style = ClassicStyle()
        self.maxfps = 60
        self.screenSize = [1024, 768]
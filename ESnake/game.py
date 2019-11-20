from .player import Player
from .pygameengine import PyGameEngine
from .helpers import *
from .styles import *

class Game:
    def __init__(self, config):
        self.name = "ESnake"
        self.state = ""
        self.style = config.style
        self.config = config
        self.player = Player()
        self.engine = PyGameEngine()

        self.components = []
        self.components.append(self.engine)
        self.components.append(self.player)

    def run(self):
        try:
            self.state = "initializing"
            self.initializeComponents()

            self.state = "running"
            self.engine.run(self)
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"

    def initializeComponents(self):
        for component in self.components:
            if hasFunction(component, "init"):
                component.init(self)

    def updateComponents(self):
        for component in self.components:
            if hasFunction(component, "update"):
                component.update(self)
            elif callable(component):
                component(self)
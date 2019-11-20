import enum
from .player import Player
from .helpers import *
from .appscreen import AppScreen

class App:
    def __init__(self, engine, config):
        self.name = "ESnake"
        self.state = ""
        self.screen = AppScreen.Loading
        self.config = config
        self.player = Player()
        self.engine = engine
        self.score = 0

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
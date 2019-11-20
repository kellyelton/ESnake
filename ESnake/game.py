from .player import Player
from .pygameengine import PyGameEngine
from .helpers import *
from .styles import *

class Game:
    def __init__(self):
        self.name = "ESnake"
        self.state = ""
        self.style = ClassicStyle()
        self.player = Player()
        self.engine = PyGameEngine()

        self.components = []
        self.components.append(self.engine)
        self.components.append(self.player)

    def run(self):
        try:
            self.state = "initializing"
            for component in self.components:
                if hasFunction(component, "init"):
                    component.init(self)

            self.state = "running"
            self.engine.run(self)

            while self.state == "running":

                self.stop()
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"

    def updateComponents(self):
        for component in self.components:
            if hasFunction(component, "update"):
                component.update(self)
            else:
                component(self)

            if hasFunction(component, "draw"):
                component.draw(self)
from .player import Player
from .input import PyGameInput
from .pygameengine import PyGameEngine
from .helpers import *

class Game:
    def __init__(self):
        self.state = ""
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

            self.state = "starting"
            for component in self.components:
                if hasFunction(component, "start"):
                    component.start(self)

            self.state = "running"
            while self.state == "running":
                for component in self.components:
                    if hasFunction(component, "update"):
                        component.update(self)
                    else:
                        component(self)

                    if hasFunction(component, "draw"):
                        component.draw(self)

                self.stop()
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"
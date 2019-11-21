import enum
from .helpers import *
from .appscreen import AppScreen

class App:
    def __init__(self, engine, config):
        self.name = "ESnake"
        self.state = ""
        self.screen = AppScreen.Loading
        self.config = config
        self.engine = engine
        self.score = 0
    def run(self):
        try:
            self.state = "initializing"
            self.engine.init(self)

            self.state = "running"
            self.engine.run(self)
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"
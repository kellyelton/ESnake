from .player import Player
from .input import PyGameInput

class Game:
    def __init__(self):
        self.state = ""
        self.player = Player()

        self.components = []
        self.components.append(PyGameInput())
        self.components.append(self.player)

    def run(self):
        self.state = "running"

        try:
            while self.state == "running":
                for component in self.components:
                    update_method = getattr(component, "update")
                    if update_method != None and callable(update_method):
                        component.update(self)
                    else:
                        component(self)
                self.stop()
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"
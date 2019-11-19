from .player import Player
from .input import PyGameInput
from .pygameengine import PyGameEngine

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
                init_method = getattr(component, "init", None)
                if init_method != None and callable(init_method):
                    component.init(self)

            self.state = "starting"
            for component in self.components:
                start_method = getattr(component, "start", None)
                if start_method != None and callable(start_method):
                    component.start(self)

            self.state = "running"
            while self.state == "running":
                for component in self.components:
                    update_method = getattr(component, "update", None)
                    if update_method != None and callable(update_method):
                        component.update(self)
                    else:
                        component(self)

                    draw_method = getattr(component, "draw", None)
                    if draw_method != None and callable(draw_method ):
                        component.draw(self)

                self.stop()
        finally:
            self.state = "stopped"

    def stop(self):
        self.state = "stopping"
import pygame

class PyGameEngine:
    def __init__(self):
        pass
    def init(self, game):
        print("engine init")
        pygame.init()

        # Adds the draw method 
        game.components.append(self.draw)
    def start(self, game):
        print("engine start")
    def update(self, game):
        print("engine update")
    def draw(self, game):
        print("engine draw")
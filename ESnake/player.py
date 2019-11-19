class Player:
    def __init__(self):
        self.direction = None
    def update(self, game):
        print("player update: " + game.state)
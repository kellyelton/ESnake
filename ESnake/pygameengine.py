import pygame

class PyGameEngine:
    def init(self, game):
        print("engine init")

        pygame.init()

    def run(self, game):
        print("engine run")

        size = [1024, 768]
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption(game.name)

        while game.state == "running":
            self.processEvents(game)
            game.updateComponents()
            self.draw(game, screen)

    def processEvents(self, game):
        for event in pygame.event.get():
            print(f"process event{event}")
            if event.type == pygame.QUIT:
                game.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.player.direction = "left"
                elif event.key == pygame.K_RIGHT:
                    game.player.direction = "right"
                elif event.key == pygame.K_UP:
                    game.player.direction = "up"
                elif event.key == pygame.K_DOWN:
                    game.player.direction = "down"
                elif event.key == pygame.K_ESCAPE:
                    game.stop()

    def draw(self, game, screen):
        screen.fill(game.style.gameBackgroundColor)
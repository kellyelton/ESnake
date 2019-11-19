import pygame

class PyGameInput:
    def update(self, game):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.player.direction = "Left"
                elif event.key == pygame.K_RIGHT:
                    game.player.direction = "Right"
                elif event.key == pygame.K_UP:
                    game.player.direction = "Up"
                elif event.key == pygame.K_DOWN:
                    game.player.direction = "Down"
import pygame
import logging
from ESnake import AppScreen, getHighScore, App, Level

class PyPostGameScreenEngine:
    def update(self, app): pass

    def __init__(self, app: App, level: Level):
        self.logger = logging.getLogger(__name__)
        self.__level = level
        self.__gameOverFont = pygame.font.Font(app.engine.style.postGameGameOverFont, app.engine.style.postGameGameOverFontSize)
        self.__scoreFont = pygame.font.Font(app.engine.style.postGameScoreFont, app.engine.style.postGameScoreFontSize)
        self.__instructionsFont = pygame.font.Font(app.engine.style.postGameInstructionsFont, app.engine.style.postGameInstructionsFontSize)

    def processEvent(self, app, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.logger.debug("pressed esc")
                app.stop()
            elif event.key == pygame.K_RETURN:
                self.logger.debug("pressed enter")
                app.screen = AppScreen.InGame

    def draw(self, app, pyscreen):
        pyscreen.fill(app.engine.style.postGameBackgroundColor)

        self.drawGameOverText(app, pyscreen)
        self.drawScoreText(app, pyscreen)
        self.drawInstructionsText(app, pyscreen)

    def drawGameOverText(self, app, pyscreen):
        gameOverText = self.__gameOverFont.render("Game Over", True, app.engine.style.postGameGameOverColor)

        gameOverTextRect = gameOverText.get_rect()
        gameOverTextRect.center = pyscreen.get_rect().midtop
        gameOverTextRect.y += 90

        pyscreen.blit(gameOverText, gameOverTextRect)

    def drawScoreText(self, app, pyscreen):
        highScore = getHighScore(app.config)

        isHighScore = highScore < self.__level.player.score

        if isHighScore:
            scoreString = "New High Score: " + str(self.__level.player.score)
        else:
            scoreString = "Score: " + str(self.__level.player.score)

        scoreText = self.__scoreFont.render(scoreString, True, app.engine.style.postGameScoreColor)

        scoreTextRect = scoreText.get_rect()
        scoreTextRect.center = pyscreen.get_rect().center

        pyscreen.blit(scoreText, scoreTextRect)

        scoreString = "High Score: " + str(highScore)

        highScoreText = self.__scoreFont.render(scoreString, True, app.engine.style.postGameScoreColor)

        highScoreTextRect = highScoreText.get_rect()
        highScoreTextRect .center = pyscreen.get_rect().center
        highScoreTextRect .y = 20 + scoreTextRect.bottom

        pyscreen.blit(highScoreText, highScoreTextRect)

    def drawInstructionsText(self, app, pyscreen):
        instructionsText = self.__instructionsFont.render("Press [Enter] to Play Again, or [Esc] to Quit", True, app.engine.style.postGameInstructionsColor)

        instructionsTextRect = instructionsText.get_rect()
        instructionsTextRect.center = pyscreen.get_rect().midbottom
        instructionsTextRect.y -= 50

        pyscreen.blit(instructionsText, instructionsTextRect)
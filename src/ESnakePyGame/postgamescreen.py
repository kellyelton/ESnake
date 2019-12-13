import pygame
import logging
from ESnake.app import App
from ESnake.appscreen import AppScreen
from ESnake.highscore import getHighScore, updateHighScore
from ESnake.level import Level

class PyPostGameScreenEngine:
    def update(self, app): pass

    def __init__(self, app: App):
        self._log = logging.getLogger(__name__)
        self.__gameOverFont = pygame.font.Font(app.engine.style.postGameGameOverFont, app.engine.style.postGameGameOverFontSize)
        self.__scoreFont = pygame.font.Font(app.engine.style.postGameScoreFont, app.engine.style.postGameScoreFontSize)
        self.__instructionsFont = pygame.font.Font(app.engine.style.postGameInstructionsFont, app.engine.style.postGameInstructionsFontSize)
        self.__oldHighScore: int = 0
        self.__playerScore: int = 0
        self.__isHighScore: bool = False

    def processEvent(self, app: App, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self._log.debug("pressed esc")
                app.stop()
            elif event.key == pygame.K_RETURN:
                self._log.debug("pressed enter")
                app.newGame()

    def start(self, app: App, time: int):
        self.__oldHighScore = getHighScore(app.config)

        self.__playerScore = app.session.level.player.score

        storedHighScore = updateHighScore(app.config, self.__playerScore)

        if storedHighScore:
            self._log.debug(f"Got a new high score of {self.__playerScore}, surpassing old high score of {self.__oldHighScore}")
            self.__isHighScore = True

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

    def drawScoreText(self, app: App, pyscreen):
        if self.__isHighScore:
            scoreString = "New High Score: " + str(self.__playerScore)
            highScore = self.__playerScore
        else:
            scoreString = "Score: " + str(self.__playerScore)
            highScore = self.__oldHighScore

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
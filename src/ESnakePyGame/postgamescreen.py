import pygame
import logging
from ESnake.level import Level
from ESnakePyGame.engine import PyGameEngine
from ESnakePyGame.highscore import getHighScore, updateHighScore

class PyPostGameScreenEngine:
    def update(self, time: int): pass

    def __init__(self, engine: PyGameEngine):
        self._log = logging.getLogger(__name__)
        self.__engine: PyGameEngine = engine
        self.__gameOverFont = pygame.font.Font(engine.style.postGameGameOverFont, engine.style.postGameGameOverFontSize)
        self.__scoreFont = pygame.font.Font(engine.style.postGameScoreFont, engine.style.postGameScoreFontSize)
        self.__instructionsFont = pygame.font.Font(engine.style.postGameInstructionsFont, engine.style.postGameInstructionsFontSize)
        self.__oldHighScore: int = 0
        self.__playerScore: int = 0
        self.__isHighScore: bool = False

    def processEvent(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self._log.debug("pressed esc")
                self.__engine.shutdown()
            elif event.key == pygame.K_RETURN:
                self._log.debug("pressed enter")
                self.__engine.newGame()

    def start(self, time: int):
        self.__oldHighScore = getHighScore(self.__engine.config)

        self.__playerScore = self.__engine.session.level.player.score

        storedHighScore = updateHighScore(self.__engine.config, self.__playerScore)

        if storedHighScore:
            self._log.debug(f"Got a new high score of {self.__playerScore}, surpassing old high score of {self.__oldHighScore}")
            self.__isHighScore = True

    def draw(self, pyscreen, time: int):
        pyscreen.fill(self.__engine.style.postGameBackgroundColor)

        self.drawGameOverText(pyscreen)
        self.drawScoreText(pyscreen)
        self.drawInstructionsText(pyscreen)

    def drawGameOverText(self, pyscreen):
        gameOverText = self.__gameOverFont.render("Game Over", True, self.__engine.style.postGameGameOverColor)

        gameOverTextRect = gameOverText.get_rect()
        gameOverTextRect.center = pyscreen.get_rect().midtop
        gameOverTextRect.y += 90

        pyscreen.blit(gameOverText, gameOverTextRect)

    def drawScoreText(self, pyscreen):
        if self.__isHighScore:
            scoreString = "New High Score: " + str(self.__playerScore)
            highScore = self.__playerScore
        else:
            scoreString = "Score: " + str(self.__playerScore)
            highScore = self.__oldHighScore

        scoreText = self.__scoreFont.render(scoreString, True, self.__engine.style.postGameScoreColor)

        scoreTextRect = scoreText.get_rect()
        scoreTextRect.center = pyscreen.get_rect().center

        pyscreen.blit(scoreText, scoreTextRect)

        scoreString = "High Score: " + str(highScore)

        highScoreText = self.__scoreFont.render(scoreString, True, self.__engine.style.postGameScoreColor)

        highScoreTextRect = highScoreText.get_rect()
        highScoreTextRect .center = pyscreen.get_rect().center
        highScoreTextRect .y = 20 + scoreTextRect.bottom

        pyscreen.blit(highScoreText, highScoreTextRect)

    def drawInstructionsText(self, pyscreen):
        instructionsText = self.__instructionsFont.render("Press [Enter] to Play Again, or [Esc] to Quit", True, self.__engine.style.postGameInstructionsColor)

        instructionsTextRect = instructionsText.get_rect()
        instructionsTextRect.center = pyscreen.get_rect().midbottom
        instructionsTextRect.y -= 50

        pyscreen.blit(instructionsText, instructionsTextRect)
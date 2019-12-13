import logging
import os

def getHighScorePath():
    return os.path.join(os.getcwd(), "highscore")

def updateHighScore(config, newHighScore: int) -> bool:
    path = getHighScorePath()

    fileStream = open(path, "a+")

    try:
        fileStream.seek(0)

        highScore: int = 0

        try:
            highScoreString = fileStream.read()
            highScoreString = highScoreString.strip()
            highScore = int(highScoreString)
        except ValueError:
            # If highScoreString is empty that's normal
            if highScoreString:
                raise

            highScore = 0

        if newHighScore > highScore:
            fileStream.seek(0, 2) #end of file
            fileStream.truncate()
            fileStream.seek(0)
            fileStream.write(str(newHighScore))
            return True
        else:
            return False
    finally:
        fileStream.close()

def getHighScore(config) -> int:
    highScore: int = 0

    path = getHighScorePath()

    fileStream = open(path, "a+")

    try:
        fileStream.seek(0)

        try:
            highScoreString = fileStream.read()
            highScoreString = highScoreString.strip()
            highScore = int(highScoreString)
        except ValueError:
            # If highScoreString is empty that's normal
            if highScoreString:
                raise

            highScore = 0
    finally:
        fileStream.close()

    return highScore
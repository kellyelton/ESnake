def updateHighScore(config, newHighScore: int) -> bool:
    fileStream = open(config.highScorePath, "r+")

    try:
        highScore: int = 0

        try:
            highScoreString = fileStream.read()
            highScoreString = highScoreString.strip()
            highScore = int(highScoreString)
        except ValueError:
            #TODO if highScoreString is empty, that's fine. Otherwise log the error because that means the file is bad.
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

    fileStream = open(config.highScorePath, "r+")
    try:

        try:
            highScoreString = fileStream.read()
            highScoreString = highScoreString.strip()
            highScore = int(highScoreString)
        except ValueError:
            #TODO if highScoreString is empty, that's fine. Otherwise log the error because that means the file is bad.
            highScore = 0
    finally:
        fileStream.close()

    return highScore
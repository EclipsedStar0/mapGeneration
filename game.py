import random
import sys
import time

import guiDisplay
import map


# noinspection PyPep8Naming
class Game:
    def __init__(self):
        self.worldMap = map.Map(stageModifier=7)
        self.display = guiDisplay.Display(self)

        self.gameOver = False

        # Remember to reset the random.seed to the current timer if you use the random module through map.py, otherwise leave as is
        random.seed(time.time())
        self.runGame()

    def runTimeStep(self):
        self.display.generateDisplay()

    def runGame(self):
        while not self.gameOver:
            self.runTimeStep()

    def endGame(self):
        self.gameOver = True
        print('Game ended')
        sys.exit()

    def getWorldGen(self):
        return self.worldMap

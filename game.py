import math
import random
import sys
import time

import civilization
import guiDisplay
import map


# noinspection PyPep8Naming
class Game:
    def __init__(self):
        self.worldMap = map.Map(gameObj=self, stageModifier=7)
        self.worldMap.generateMap()
        self.display = guiDisplay.Display(self)

        self.civilizationDict = dict()

        random.seed(5779)
        civsInPlay = 1
        riverDict = self.worldMap.getRiverData()
        columns, rows = self.worldMap.getColumns(), self.worldMap.getRows()
        terrainData = self.worldMap.getTerrainData()
        waterTerrain = self.worldMap.getWaterTerrainTypes()
        eulersNumber = math.e
        for newCiv in range(0, civsInPlay):
            randomID = random.randint(100000000, 999999999)
            while randomID in self.civilizationDict:
                randomID = random.randint(100000000, 999999999)
            validRiver, vWARR = [], []
            for region in riverDict:
                for river in riverDict.get(region):
                    minDist = float('inf')
                    rStart = riverDict.get(region).get(river).get("Start")
                    riverX, riverY = rStart % columns, int(rStart / rows)
                    for civID in self.civilizationDict:
                        civObj = self.civilizationDict.get(civID)
                        civCap = civObj.getCapital()
                        civX, civY = civCap % columns, int(civCap / columns)
                        minDist = min(minDist, pow(pow(civX - riverX, 2) + pow(civY - riverY, 2), 0.5))
                    if minDist >= 50:
                        validRiver.append((river, region))
                        vWARR.append(pow(len(riverDict.get(region).get(river).get("Nodes")), 1.35))
            chosenRiver = random.choices(validRiver, vWARR, k=1)[0]
            cRData = riverDict.get(chosenRiver[1]).get(chosenRiver[0]).get("Nodes")
            nodeArr, waterArr = [], []
            for node in cRData:
                nodeObj = terrainData.get(node)
                nodeTerrain = nodeObj.getTerrainType()
                nodeWaterScore = 0
                nodeArr.append(node)
                if nodeTerrain not in waterTerrain:
                    # To ensure we don't get negative weights whilst keeping same weighting / Normalizing weights
                    nodeWaterScore = pow(eulersNumber, nodeObj.getWaterScore())
                waterArr.append(nodeWaterScore)
            chosenNode = random.choices(nodeArr, waterArr, k=1)[0]

            self.civilizationDict[randomID] = civilization.Civilization(self, randomID)
            self.civilizationDict.get(randomID).setCapital(chosenNode)

        self.gameOver = False

        # Remember to reset the random.seed to the current timer if you use the random module through map.py, otherwise leave as is
        # random.seed(time.time())
        self.runGame()

    def runTimeStep(self):

        # Update Everything

        # Generate display of most recent data
        self.display.generateDisplay()

        # Player Action

        # Antagonist Action

    def runGame(self):
        while not self.gameOver:
            self.runTimeStep()

    def endGame(self):
        self.gameOver = True
        print('Game ended')
        sys.exit()

    def getWorldGen(self):
        return self.worldMap

    def fetchWorldGenTerrainData(self):
        return self.getWorldGen().getTerrainData()

    def getCivilizationDict(self):
        return self.civilizationDict

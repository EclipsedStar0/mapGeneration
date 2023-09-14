import math
import random
import sys
import time
import pygame

import customThread


# noinspection PyPep8Naming
class Map:
    def __init__(self):
        self.width = 1024
        self.height = 576

        # You can change the adjustFactor to easily scale the map, so a factor of 2, would make it 4 times smaller, 4 would make it 16 times smaller, 8 would make it 64 times smaller, etc.
        self.adjustFactor = 16

        # For optimal generation, keep radial search between 0 and 5, increase slightly if you drop adjust factor
        self.radialSearch = int(32/self.adjustFactor)

        self.multiThreading = False

        self.columns, self.rows = 1024 // self.adjustFactor, 576 // self.adjustFactor
        # self.columns, self.rows = 256, 144
        # self.columns, self.rows = 32, 18
        pygame.init()
        self.elevationGrid = dict()

        # Seed must have all 0-9 numbers, and be within 24 digits

        seed = 544786120398304714620491
        random.seed(seed)

        # self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor+self.adjustFactor*8))

        self.terrainTypes = {
            "Ice": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.05,
                "Color": (255, 255, 255),
                "PTQ": (0, 25),
                "HPTQ": (0, 28)
            },
            "Tundra": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (230, 230, 230),
                "PTQ": (23, 35),
                "HPTQ": (15, 55)
            },
            "Taiga": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.25,
                "Color": (160, 180, 160),
                "PTQ": (25, 35),
                "HPTQ": (17, 59)
            },
            "Forest": {
                "RegionSelChance": 20,
                "NodeSelChance": 20,
                "Diffusion": 0.25,
                "Color": (0, 60, 0),
                "PTQ": (44, 63),
                "HPTQ": (34, 85)
            },
            "Grassland": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.10,
                "Color": (70, 200, 50),
                "PTQ": (43, 68),
                "HPTQ": (33, 86)
            },
            "Plains": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (150, 200, 50),
                "PTQ": (65, 85),
                "HPTQ": (55, 90)
            },
            "Desert": {
                "RegionSelChance": 20,
                "NodeSelChance": 25,
                "Diffusion": -0.05,
                "Color": (220, 190, 50),
                "PTQ": (80, 100),
                "HPTQ": (75, 100)
            },
            "Oasis": {
                "RegionSelChance": 20,
                "NodeSelChance": 0.25,
                "Diffusion": -0.05,
                "Color": (30, 175, 140),
                "PTQ": (90, 100),
                "HPTQ": (80, 100)
            },
            "Hills": {
                "RegionSelChance": 20,
                "NodeSelChance": 10,
                "Diffusion": -0.10,
                "Color": (170, 150, 50),
                "PTQ": (35, 95),
                "HPTQ": (33, 100)
            },
            "Mountains": {
                "RegionSelChance": 30,
                "NodeSelChance": 5,
                "Diffusion": -0.15,
                "Color": (50, 50, 70),
                "PTQ": (35, 85),
                "HPTQ": (30, 95)
            }
        }

        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = 0
        self.nodeTerrainData = dict()

        startTime = time.time()
        print('Begining generation...')
        self.generateMap()
        print(f'We finished map generation-- this took {time.time()-startTime} seconds')

        self.SCREEN = pygame.display.set_mode((self.width, self.height))
        self.generateDisplay()

    def generateMap(self):

        def distToSplit(nodeNum1, nodeNum2):
            nodeNum1x, nodeNum1y = nodeNum1 % self.columns, int(nodeNum1 / self.columns)
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        def distToGiven(nodeNum1x, nodeNum1y, nodeNum2x, nodeNum2y):
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        instancedNodes = dict()

        for row in range(0, self.rows):

            # Get base weights based off of lattitude

            lattitudePQT = 100 - abs(1 - 2 * row / self.rows) * 100
            terrainWeightArr = dict()

            for terrainEntry in self.terrainTypes:
                terrainPTQ = self.terrainTypes.get(terrainEntry).get("PTQ")
                terrainHPTQ = self.terrainTypes.get(terrainEntry).get("HPTQ")
                if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 1.1), 1)
                    terrainWeightArr[terrainEntry] = fetchedWeight
                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 2.5), 1)
                    terrainWeightArr[terrainEntry] = fetchedWeight

            for column in range(0, self.columns):
                nodeNum = row * self.columns + column
                self.nodeTerrainData[nodeNum] = dict()
                self.nodeTerrainData[nodeNum]["Weights"] = terrainWeightArr
            if len(terrainWeightArr) < 1:
                print("Missing potential selection!!")
                raise Exception

        maxNodes = self.columns * self.rows

        while len(instancedNodes) < maxNodes:
            nodeNum = random.randint(0, maxNodes-1)
            while nodeNum in instancedNodes:
                nodeNum = random.randint(0, maxNodes-1)
            nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns

            # print("---Different Node Num----")
            # print(100 - abs(1 - 2 * nodeY / self.rows) * 100)

            diffuseThreads = []

            for cY in range(max(nodeY - self.radialSearch, 0), min(nodeY + self.radialSearch, self.rows)):
                for cX in range(max(nodeX - self.radialSearch, 0), min(nodeX + self.radialSearch, self.columns)):
                    diffuseNodeNum = cY * self.columns + cX
                    if diffuseNodeNum in instancedNodes and diffuseNodeNum != nodeNum:
                        if self.multiThreading:
                            newThread = customThread.mapRadialSearchThread(nodeX, nodeY, cX, cY, self.rows, self.columns, self.radialSearch, self.terrainTypes, self.nodeTerrainData)
                            newThread.start()
                            diffuseThreads.append(newThread)
                        else:
                            distToDiffuseNode = distToGiven(nodeX, nodeY, cX, cY)
                            if distToDiffuseNode <= self.radialSearch:
                                # We fall within the boundaries to affect this node
                                diffuseTerrainInfo = self.nodeTerrainData.get(diffuseNodeNum)
                                diffuseTerrain = diffuseTerrainInfo.get("ChosenTerrain")
                                terrainPTQ = self.terrainTypes.get(diffuseTerrain).get("PTQ")
                                terrainHPTQ = self.terrainTypes.get(diffuseTerrain).get("HPTQ")
                                lattitudePQT = 100 - abs(1 - 2 * cY / self.rows) * 100

                                diffuseWeight = self.terrainTypes.get(diffuseTerrain).get("NodeSelChance")
                                if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                                    diffuseWeight = self.terrainTypes.get(diffuseTerrain).get("NodeSelChance")
                                    # Fetch our distance from the center of the range
                                    temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 50
                                    diffuseWeight = max(diffuseWeight - pow(temp, 1.1), 1)
                                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                                    diffuseWeight = self.terrainTypes.get(diffuseTerrain).get("NodeSelChance")
                                    # Fetch our distance from the center of the range
                                    temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 50
                                    diffuseWeight = max(diffuseWeight - pow(temp, 2.5), 1)
                                else:
                                    diffuseWeight *= 0.25

                                diffuseWeight = diffuseWeight / pow(distToDiffuseNode, 0.7)

                                if diffuseTerrain not in self.nodeTerrainData.get(nodeNum).get("Weights"):
                                    self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = diffuseWeight
                                else:
                                    self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = pow(pow(diffuseWeight, 2) + pow(self.nodeTerrainData.get(nodeNum).get("Weights").get(diffuseTerrain), 2), 0.5)

            if self.multiThreading:
                for thread in diffuseThreads:
                    thread.join()
                    diffuseWeight, diffuseTerrain, mode = thread.getVal()
                    if mode:
                        if diffuseTerrain not in self.nodeTerrainData.get(nodeNum).get("Weights"):
                            self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = diffuseWeight
                        else:
                            self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = pow(pow(diffuseWeight, 2) + pow(
                                self.nodeTerrainData.get(nodeNum).get("Weights").get(diffuseTerrain), 2), 0.5)

            proxyTArr, proxyWeightArr = [], []
            for terrainType in self.nodeTerrainData.get(nodeNum).get("Weights"):
                proxyTArr.append(terrainType)
                proxyWeightArr.append(self.nodeTerrainData.get(nodeNum).get("Weights").get(terrainType))
            try:
                designatedTerrain = random.choices(proxyTArr, proxyWeightArr, k=1)[0]
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                instancedNodes[nodeNum] = True
            except ValueError:
                print(proxyTArr)
                print(proxyWeightArr)
                print(self.nodeTerrainData.get(nodeNum))
                print(len(instancedNodes))
                raise Exception

    def generateMapOld1(self):
        for row in range(0, self.rows):
            lattitudePQT = 100 - abs(1 - 2 * row / self.rows) * 100
            allowedTerrainsForLAT = []
            allowedTerrainsWeight = []

            for terrainEntry in self.terrainTypes:
                terrainPTQ = self.terrainTypes.get(terrainEntry).get("PTQ")
                terrainHPTQ = self.terrainTypes.get(terrainEntry).get("HPTQ")
                if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                    allowedTerrainsForLAT.append(terrainEntry)
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0])/2))/20
                    fetchedWeight = max(fetchedWeight - pow(temp, 1.1), 1)
                    allowedTerrainsWeight.append(fetchedWeight)
                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                    allowedTerrainsForLAT.append(terrainEntry)
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 2.5), 1)
                    allowedTerrainsWeight.append(fetchedWeight)
            for column in range(0, self.columns):
                nodeNum = row * self.columns + column
                designatedTerrain = random.choices(allowedTerrainsForLAT, allowedTerrainsWeight, k=1)[0]
                self.nodeTerrainData[nodeNum] = dict()
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain

    # noinspection PyPep8Naming
    def generateMapOld(self):
        terrainArr2 = []
        for terrainType2 in self.terrainTypes:
            terrainArr2.append(terrainType2)

        def distTo(nodeNum1, nodeNum2):
            nodeNum1x, nodeNum1y = nodeNum1 % self.columns, int(nodeNum1 / self.columns)
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        def assignRegions(terrainArr, regionSpawnTile):
            output = None
            proxyTArr = []
            designatedWeightsArr = []
            for terrainType in self.terrainTypes:
                weight = pow(self.terrainTypes.get(terrainType).get("RegionSelChance")/(self.terrainRecord.get(terrainType) + 1), 0.4)
                designatedWeightsArr.append(weight)

            output = random.choices(terrainArr, designatedWeightsArr, k=1)[0]
            self.terrainRecord[output] += 1
            return output

        nodeTerrainData = dict()

        regionSpawnTiles = []
        maxNodes = self.rows*self.height
        for currentRegionSpawn in range(int(pow(self.rows*self.height, 0.4))):
            randomNode = random.randint(0, maxNodes - 1)
            while randomNode in regionSpawnTiles:
                randomNode = random.randint(0, maxNodes - 1)
            regionSpawnTiles.append(randomNode)

        for regionSpawn in regionSpawnTiles:
            nodeTerrainData[regionSpawn] = dict()
            designatedTerrain = assignRegions(terrainArr2, regionSpawn)
            nodeTerrainData[regionSpawn]["ChosenTerrain"] = designatedTerrain
            nodeTerrainData[regionSpawn]["Weight"] = [self.terrainTypes.get(designatedTerrain).get("NodeSelChance")]

        for currentIteration in range(0, maxNodes - len(regionSpawnTiles)):
            selectedNode = random.randint(0, maxNodes - 1)
            success = False
            while not success:
                if selectedNode in regionSpawnTiles or selectedNode in nodeTerrainData:
                    if "ChosenTerrain" not in nodeTerrainData.get(selectedNode):
                        success = True
                        nodeTerrainData[selectedNode] = dict()
                    else:
                        selectedNode = random.randint(0, maxNodes - 1)
                else:
                    success = True
                    nodeTerrainData[selectedNode] = dict()

            nodeTerrainData[selectedNode]["Weight"] = dict()

            # This part can be parallelized
            for regionSpawn in regionSpawnTiles:
                distance = distTo(selectedNode, regionSpawn)
                regionTerrain = nodeTerrainData.get(regionSpawn).get("ChosenTerrain")
                weightUsed = self.terrainTypes.get(regionTerrain).get("NodeSelChance")-pow(distance, 1.2 - self.terrainTypes.get(regionTerrain).get("Diffusion"))
                if distance > 10:
                    weightUsed = max(weightUsed, pow(2*(pow(distance, 2.7)/pow(distance, 3)), 7))
                if regionTerrain not in nodeTerrainData.get(selectedNode).get("Weight"):
                    nodeTerrainData[selectedNode]["Weight"][regionTerrain] = weightUsed
                else:
                    nodeTerrainData[selectedNode]["Weight"][regionTerrain] += weightUsed

            proxyArrForTerrain = []
            proxyArrForWeight = []
            for regionTerrain in nodeTerrainData.get(selectedNode).get("Weight"):
                proxyArrForTerrain.append(regionTerrain)
                proxyArrForWeight.append(nodeTerrainData.get(selectedNode).get("Weight").get(regionTerrain))
            selectedTerrain = random.choices(proxyArrForTerrain, proxyArrForWeight, k=1)[0]
            nodeTerrainData[selectedNode]["ChosenTerrain"] = selectedTerrain

        self.nodeTerrainData = nodeTerrainData

    def generateDisplay(self):
        pass
        ''' Draw the display '''

        def drawTheInterface():
            self.SCREEN.fill((20, 10, 30))
            for row in range(0, self.rows):
                for column in range(0, self.columns):
                    nodeNum = row * self.columns + column
                    color = self.terrainTypes.get(self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")).get("Color")
                    pygame.draw.rect(self.SCREEN, color, (self.adjustFactor * column, self.adjustFactor * row, self.adjustFactor, self.adjustFactor))

        drawTheInterface()
        pygame.display.update()

        '''User Interactions'''

        success = False
        while not success:
            for userEvent in pygame.event.get():
                pos = pygame.mouse.get_pos()
                playerRect = pygame.Rect(pos[0] - 1, pos[1] - 1, 2, 2)

                if userEvent.type == pygame.QUIT:
                    sys.exit()

    def fetchTerrainData(self):
        return self.nodeTerrainData

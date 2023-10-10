import math
import random
import time
from copy import deepcopy

import pygame

import customThread
import node
import terrainCodex


# noinspection PyPep8Naming
class Map:
    def __init__(self, gameObj, stageModifier=7, seedPara=None):
        self.gameObj = gameObj
        self.width = 1024
        self.height = 576

        # You can change the adjustFactor to easily scale the map, so a factor of 2, would make it 4 times smaller, 4 would make it 16 times smaller, 8 would make it 64 times smaller, etc.
        self.adjustFactor = 4

        # For optimal generation, keep radial search between 0 and 5, increase slightly if you drop adjust factor
        self.radialSearch = min(int(32 / self.adjustFactor), 4)
        # self.radialSearch = 4

        # Computation Time Alert: Adjust 2, Radial 6 has a time of 28.9 seconds
        # Be Advised: Adjust 1, Radial 32 has a time exceeding known limits (+30 minutes)
        # A1, R4 has a time of 58.19 seconds

        # Note-- certain mulithreading operations very ineffective, whilst others are, so those ineffective ones are being disabled
        self.multiThreading = True

        self.columns, self.rows = 1024 // self.adjustFactor, 576 // self.adjustFactor
        # self.columns, self.rows = 256, 144
        # self.columns, self.rows = 32, 18
        pygame.init()
        self.elevationGrid = dict()

        # Seed must have all 0-9 numbers, and be within 24 digits

        seed = 544786120398304714620491
        if seedPara is None and not isinstance(seed, int):
            seed = random.randint(100000000000000000000000, 999999999999999999999999)
            self.savedSeed = seed
        elif seedPara is None:
            self.savedSeed = seed
        else:
            self.savedSeed = seedPara
        random.seed(self.savedSeed)
        # random.seed(time.time())

        # self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor+self.adjustFactor*8))

        self.terrainCodex = terrainCodex.TerrainCodex()
        self.terrainTypes = self.terrainCodex.getCodex()

        self.terrainTypesELE = ["Mountains", "Hills", "Steppe"]
        self.terrainTypesWAT = ["Ocean", "Coastal", "Oasis", "Ice"]

        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = set()
        self.nodeTerrainData = dict()

        self.continentData = dict()
        self.regionData = dict()
        self.riverDict = dict()

        # Set to 0 to only do base spread
        # Set to 1 to do diffusion
        # Set to 2 to also do heightmap
        # Set to 3 to do coastal conversion w/elevation
        # Set to 4 to do coastal conversion w/proximity
        # Set to 5 to do Continent Organization
        # Set to 6 to do Region Organization
        self.stageModifier = stageModifier

    def generateMap(self):
        startTime = time.time()
        print('Begining generation...')

        # NOTE-- we are redefining these here incase we regenerate the map in the GUI to advance a stage
        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = set()
        self.nodeTerrainData = dict()

        self.continentData = dict()
        self.regionData = dict()
        # We need to reset the seed to what we saved it as
        random.seed(self.savedSeed)

        def distToSplit(nodeNum1, nodeNum2):
            nodeNum1x, nodeNum1y = nodeNum1 % self.columns, int(nodeNum1 / self.columns)
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x - nodeNum1x, 2) + pow(nodeNum2y - nodeNum1y, 2), 0.5)

        def distToGiven(nodeNum1x, nodeNum1y, nodeNum2x, nodeNum2y):
            return pow(pow(nodeNum2x - nodeNum1x, 2) + pow(nodeNum2y - nodeNum1y, 2), 0.5)

        instancedNodes = dict()

        waterNodes = set()
        print('Assigning Base Weights...')
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
                    temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 1.1), 0)
                    terrainWeightArr[terrainEntry] = fetchedWeight
                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 2.5), 0)
                    terrainWeightArr[terrainEntry] = fetchedWeight

            if self.stageModifier <= 0:
                for column in range(0, self.columns):
                    nodeNum = row * self.columns + column
                    self.nodeTerrainData[nodeNum] = dict()
                    self.nodeTerrainData[nodeNum]["Weights"] = terrainWeightArr

                    if self.stageModifier <= 0:
                        designatedTerrain = random.choices(list(terrainWeightArr.keys()), list(terrainWeightArr.values()), k=1)[0]
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                    self.nodeTerrainData[nodeNum]["WaterScore"] = 0
                    self.nodeTerrainData[nodeNum]["Lattitude"] = lattitudePQT
            else:
                for column in range(0, self.columns):
                    nodeNum = row * self.columns + column
                    self.nodeTerrainData[nodeNum] = dict()
                    self.nodeTerrainData[nodeNum]["Weights"] = terrainWeightArr
                    self.nodeTerrainData[nodeNum]["WaterScore"] = 0
                    self.nodeTerrainData[nodeNum]["Lattitude"] = lattitudePQT
                randomChance = random.randint(0, 100)
                if randomChance > 45:
                    nodeNum = row*self.columns + random.randint(0, self.columns-1)
                    tWeightArr = []
                    tTypeArr = []
                    for terrainEntry in self.terrainTypes:
                        terrainPTQ = self.terrainTypes.get(terrainEntry).get("PTQ")
                        terrainHPTQ = self.terrainTypes.get(terrainEntry).get("HPTQ")
                        if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                            fetchedWeight = self.terrainTypes.get(terrainEntry).get("RegionSelChance")
                            # Fetch our distance from the center of the range
                            temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 20
                            fetchedWeight = max(fetchedWeight - pow(temp, 1.1), 0)
                            tWeightArr.append(fetchedWeight)
                            tTypeArr.append(terrainEntry)
                        elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                            fetchedWeight = self.terrainTypes.get(terrainEntry).get("RegionSelChance")
                            # Fetch our distance from the center of the range
                            temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 20
                            fetchedWeight = max(fetchedWeight - pow(temp, 2.5), 0)
                            tWeightArr.append(fetchedWeight)
                            tTypeArr.append(terrainEntry)
                    designatedTerrain = random.choices(tTypeArr, tWeightArr, k=1)[0]
                    self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                    if designatedTerrain not in self.terrainRecord:
                        self.terrainRecord[designatedTerrain] = set()
                    self.terrainRecord[designatedTerrain].add(nodeNum)
                    instancedNodes[nodeNum] = True
                    if designatedTerrain == "Ocean" or designatedTerrain == "Coastal":
                        waterNodes.add(nodeNum)

            if len(terrainWeightArr) < 1:
                print("Missing potential selection!!")
                raise Exception

        maxNodes = self.columns * self.rows

        if self.stageModifier > 0:
            print('Begining Diffusion...')
            while len(instancedNodes) < maxNodes:
                nodeNum = random.randint(0, maxNodes - 1)
                while nodeNum in instancedNodes:
                    nodeNum = random.randint(0, maxNodes - 1)
                nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns

                # print("---Different Node Num----")
                # print(100 - abs(1 - 2 * nodeY / self.rows) * 100)

                diffuseThreads = []

                for elemY in range(nodeY - self.radialSearch, nodeY + self.radialSearch + 1):
                    cY = elemY % self.rows
                    for elemX in range(nodeX - self.radialSearch, nodeX + self.radialSearch + 1):
                        cX = elemX % self.columns
                        diffuseNodeNum = cY * self.columns + cX
                        if diffuseNodeNum in instancedNodes and diffuseNodeNum != nodeNum:
                            # This thread is very ineffective
                            if self.multiThreading and False:
                                newThread = customThread.mapRadialSearchThread(nodeX, nodeY, cX, cY, self.rows, self.columns, self.radialSearch, self.terrainTypes, self.nodeTerrainData)
                                newThread.start()
                                diffuseThreads.append(newThread)
                            else:
                                if elemY * self.columns + elemX == diffuseNodeNum:
                                    distToDiffuseNode = distToGiven(nodeX, nodeY, elemX, elemY)
                                else:
                                    distToDiffuseNode = distToGiven(nodeX, nodeY, cX, cY)
                                if distToDiffuseNode <= self.radialSearch:
                                    # We fall within the boundaries to affect this node
                                    diffuseTerrainInfo = self.nodeTerrainData.get(diffuseNodeNum)
                                    diffuseTerrain = diffuseTerrainInfo.get("ChosenTerrain")
                                    terrainPTQ = self.terrainTypes.get(diffuseTerrain).get("PTQ")
                                    terrainHPTQ = self.terrainTypes.get(diffuseTerrain).get("HPTQ")
                                    # lattitudePQT = 100 - abs(1 - 2 * cY / self.rows) * 100
                                    lattitudePQT = diffuseTerrainInfo.get("Lattitude")

                                    diffuseWeight = self.terrainTypes.get(diffuseTerrain).get("NodeSelChance")
                                    diffusionVal = self.terrainTypes.get(diffuseTerrain).get("Diffusion")
                                    if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                                        # Fetch our distance from the center of the range
                                        temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 50
                                        diffuseWeight = max(diffuseWeight - pow(temp, 1.1), 0)
                                    elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                                        # Fetch our distance from the center of the range
                                        temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                                        diffuseWeight = max(diffuseWeight - pow(temp, 2.5), 0)
                                    else:
                                        temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                                        diffuseWeight = 0.25 * max(diffuseWeight - pow(temp, 3.25), 0)
                                    if diffuseWeight > 0:
                                        diffuseWeight = diffuseWeight + pow(diffuseWeight, diffusionVal)
                                        # diffuseWeight *= 0.25
                                        diffuseWeight = diffuseWeight / pow(distToDiffuseNode + 1, 0.7)
                                        if diffuseWeight >= 1:
                                            diffuseWeight = pow(diffuseWeight, diffusionVal + 1)
                                    else: diffuseWeight = 0

                                    if diffuseTerrain not in self.nodeTerrainData.get(nodeNum).get("Weights"):
                                        self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = diffuseWeight
                                    else:
                                        self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = pow(pow(diffuseWeight, 2) + pow(self.nodeTerrainData.get(nodeNum).get("Weights").get(diffuseTerrain), 2), 0.5)

                # Currently, multithreading is slower than doing it manually, this may be due to unoptimized code
                if self.multiThreading and False:
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
                    if designatedTerrain not in self.terrainRecord:
                        self.terrainRecord[designatedTerrain] = set()
                    self.terrainRecord[designatedTerrain].add(nodeNum)
                    instancedNodes[nodeNum] = True
                    if designatedTerrain in self.terrainTypesWAT:
                        waterNodes.add(nodeNum)
                except ValueError:
                    print(proxyTArr)
                    print(proxyWeightArr)
                    print(self.nodeTerrainData.get(nodeNum))
                    print(len(instancedNodes))
                    raise Exception

            print('-Diffusion Complete')

        if self.stageModifier > 1:
            print('Begining ElevationMap...')
            elevatedNodes = []
            '''iceNodes = []
            tundraNodes = []'''

            for terrainType in self.terrainTypesELE:
                if terrainType in self.terrainRecord:
                    for nodeNum in self.terrainRecord.get(terrainType):
                        elevatedNodes.append(nodeNum)

            '''for iceNode in self.terrainRecord.get("Ice"):
                iceNodes.append(iceNode)
            for tundraNode in self.terrainRecord.get("Tundra"):
                tundraNodes.append(tundraNode)'''

            for nodeNum in elevatedNodes:
                nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                rangeBonus, effectBonus = self.terrainTypes.get(designatedTerrain).get("RangeBonus"), self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                selfBonus = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                self.elevationGrid[nodeNum] = random.randint((selfBonus - 2) * 100, (selfBonus + 3) * 100) / 100 + effectBonus
                nodeElevation = self.elevationGrid.get(nodeNum)
                self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation

                for elemY in range(nodeY - rangeBonus * 2 - random.randint(0, 1), nodeY + rangeBonus * 2 + random.randint(0, 1) + 1):
                    cY = elemY % self.rows
                    for elemX in range(nodeX - rangeBonus * 2 - random.randint(0, 1), nodeX + rangeBonus * 2 + random.randint(0, 1) + 1):
                        cX = elemX % self.columns
                        diffuseNodeNum = cY * self.columns + cX
                        if diffuseNodeNum not in elevatedNodes:
                            if elemY * self.columns + elemX == diffuseNodeNum:
                                distToDiffuseNode = distToGiven(nodeX, nodeY, elemX, elemY)
                            else:
                                distToDiffuseNode = distToGiven(nodeX, nodeY, cX, cY)
                            if distToDiffuseNode < rangeBonus * 2.9:
                                diffuseElevation = nodeElevation / pow(distToDiffuseNode, 0.7) - effectBonus / rangeBonus
                                designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                                effectBonus = int(self.terrainTypes.get(designatedTerrain).get("EffectBonus") * 0.5)
                                diffuseElevation += random.randint((-3 + effectBonus) * 100, (1 + effectBonus) * 100) / 100

                                if "Elevation" not in self.nodeTerrainData.get(diffuseNodeNum):
                                    self.nodeTerrainData[diffuseNodeNum]["Elevation"] = [diffuseElevation]
                                else:
                                    self.nodeTerrainData[diffuseNodeNum]["Elevation"].append(diffuseElevation)

            '''for nodeNum in iceNodes:
                if "Elevation" not in self.nodeTerrainData.get(nodeNum):
                    self.nodeTerrainData[nodeNum]["Elevation"] = random.randint(-4, -2)
                else:
                    self.nodeTerrainData[nodeNum]["Elevation"] += random.randint(-3, -1)

            for nodeNum in tundraNodes:
                if "Elevation" not in self.nodeTerrainData.get(nodeNum):
                    self.nodeTerrainData[nodeNum]["Elevation"] = random.randint(-3, -1)
                else:
                    self.nodeTerrainData[nodeNum]["Elevation"] += random.randint(-2, 0)'''

            for nodeNum in self.nodeTerrainData:
                if nodeNum not in elevatedNodes:
                    if "Elevation" not in self.nodeTerrainData.get(nodeNum):
                        designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                        effectBonus = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                        if effectBonus is None: effectBonus = 0
                        self.elevationGrid[nodeNum] = random.randint((-3 + effectBonus)*100, (1 + effectBonus)*100) / 100
                        self.nodeTerrainData[nodeNum]["Elevation"] = self.elevationGrid.get(nodeNum)
                    else:
                        nodeElevation = sorted(self.nodeTerrainData.get(nodeNum).get("Elevation"))
                        if len(nodeElevation) > 1:
                            self.nodeTerrainData[nodeNum]["Elevation"] = sum(nodeElevation) / len(nodeElevation) + nodeElevation[-1] / (len(nodeElevation) - 1)
                        else:
                            ranEle = random.randint(-1, 3)
                            self.nodeTerrainData[nodeNum]["Elevation"] = (nodeElevation[0] + ranEle) / 2 + ranEle / (2-1)
                        self.elevationGrid[nodeNum] = self.nodeTerrainData.get(nodeNum).get("Elevation")
            print('-ElevationMap Complete')

        if self.stageModifier > 2:
            print('Begining Coastal Conversion w/ Elevation')
            for terrainType in self.terrainTypesWAT:
                if terrainType in self.terrainRecord:
                    for nodeNum in self.terrainRecord.get(terrainType):
                        waterNodes.add(nodeNum)

            '''Currently, default approach is faster than multithreading'''
            # 15.4 / 3 (Multi) > 1.24300 / 3 (Default)
            # This approach also seems to create slight deviations from the default approach
            if self.multiThreading and False:
                runningThreads = []
                for nodeNum in self.nodeTerrainData:
                    newThread = customThread.mapCoastalConverEle(nodeNum, self.nodeTerrainData, self.terrainTypes, self.terrainRecord)
                    newThread.start()
                    runningThreads.append(newThread)
                for newThread in runningThreads:
                    newThread.join()
                    values = newThread.getVal()
                    newTerrain = values[0]
                    if isinstance(values[0], list):
                        newTerrain = random.choices(values[0], k=1)[0]
                    if newTerrain != values[1]:
                        self.terrainRecord[values[1]].remove(values[2])
                        self.nodeTerrainData[values[2]]["ChosenTerrain"] = newTerrain
                        self.terrainRecord[newTerrain].add(values[2])
                        if newTerrain in self.terrainTypesWAT:
                            waterNodes.add(values[2])
                    elif newTerrain in self.terrainTypesWAT:
                        waterNodes.add(values[2])

            else:
                for nodeNum in self.nodeTerrainData:
                    designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    if nodeElevation < -4 and designatedTerrain != "Ocean":
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = "Ocean"
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                        waterNodes.add(nodeNum)
                    elif nodeElevation < 1.5 and designatedTerrain != "Coastal":
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = "Coastal"
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                        waterNodes.add(nodeNum)
                    elif nodeElevation < 4 and nodeNum not in waterNodes:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                        if designatedTerrain in self.terrainTypesWAT:
                            waterNodes.add(nodeNum)
                    elif nodeElevation > 10:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Dry"), k=1)[0]
                        valid = True
                        if self.nodeTerrainData.get(nodeNum).get("Lattitude") < 70:
                            if self.terrainTypes.get(designatedTerrain).get("WaterScore") <= -1:
                                self.terrainRecord[self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")].add(nodeNum)
                                valid = False
                        if valid:
                            self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                            if designatedTerrain not in self.terrainRecord:
                                self.terrainRecord[designatedTerrain] = set()
                            self.terrainRecord[designatedTerrain].add(nodeNum)
            print(f'-Coastal Conversion w/ Elevation Complete')

        if self.stageModifier > 3:
            print('Begining Coastal Conversion w/ Proximity')

            ranNodesToCheck = []
            erosionFactor, erosionOverride = 4, 0
            for errosionInterval in range(erosionFactor):
                print(f'-Initiating Erosion Stage #{errosionInterval+1}')
                for nodeNum in self.nodeTerrainData:
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    # if designatedTerrain not in self.terrainTypesWAT and nodeElevation < 5:
                    if 1.45 - pow(erosionFactor, 1.2) * 1.45 < nodeElevation < max(8 * erosionFactor, erosionOverride):
                        ranNodesToCheck.append(nodeNum)

                while len(ranNodesToCheck) > 0:
                    nodeNumIndex = random.randint(0, len(ranNodesToCheck)-1)
                    nodeNum = ranNodesToCheck[nodeNumIndex]
                    del ranNodesToCheck[nodeNumIndex]

                    designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                    # breakedOutOfLoop = False
                    waterScore = self.terrainTypes.get(designatedTerrain).get("WaterScore")
                    numScoreNodes = 1
                    coastalSearchRange = 2
                    for elemY in range(nodeY - coastalSearchRange, nodeY + coastalSearchRange + 1):
                        cY = elemY % self.rows
                        for elemX in range(nodeX - coastalSearchRange, nodeX + coastalSearchRange + 1):
                            cX = elemX % self.columns
                            diffuseNodeNum = cY * self.columns + cX
                            # diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                            numScoreNodes += 1
                            # if diffuseTerrain in self.terrainTypesWAT:
                            # if diffuseNodeNum in waterNodes:

                            diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                            waterScore += (self.terrainTypes.get(diffuseTerrain).get("WaterScore"))

                            '''if not breakedOutOfLoop:
                                self.terrainRecord[designatedTerrain].remove(nodeNum)
                                designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                                self.terrainRecord[designatedTerrain].add(nodeNum)
                                breakedOutOfLoop = True'''
                    wScoreRatio = waterScore / numScoreNodes
                    self.nodeTerrainData[nodeNum]["WaterScore"] = wScoreRatio
                    if wScoreRatio > 0.75:
                        if wScoreRatio > 1.45:
                            self.terrainRecord[designatedTerrain].remove(nodeNum)
                            self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                            self.terrainRecord["Ocean"].add(nodeNum)
                            nodeElevation += self.terrainTypes.get("Ocean").get("EffectBonus")
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                            waterNodes.add(nodeNum)
                        else:
                            self.terrainRecord[designatedTerrain].remove(nodeNum)
                            self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Coastal"
                            self.terrainRecord["Coastal"].add(nodeNum)
                            nodeElevation += self.terrainTypes.get("Coastal").get("EffectBonus")
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                            waterNodes.add(nodeNum)
                    elif (wScoreRatio > 0.65 - 0.1 * min(erosionFactor, 3)) or (designatedTerrain == "Desert" and wScoreRatio > 0.65 - 0.1 * erosionFactor):
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                        bEle = 0
                        if "SelfBonus" in self.terrainTypes.get(designatedTerrain): bEle = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                        else: bEle = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                        nodeElevation += bEle / 2
                        self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                        self.elevationGrid[nodeNum] = nodeElevation
                        if wScoreRatio > 0.80 - 0.1 * min(erosionFactor, 3):
                            designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                            if "SelfBonus" in self.terrainTypes.get(designatedTerrain):
                                bEle = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                            else:
                                bEle = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                            nodeElevation += bEle / 2
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                        if designatedTerrain in self.terrainTypesWAT:
                            waterNodes.add(nodeNum)
                    elif wScoreRatio < -0.25 - erosionFactor * 0.15:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Dry"), k=1)[0]
                        bEle = 0
                        if "SelfBonus" in self.terrainTypes.get(designatedTerrain):
                            bEle = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                        else:
                            bEle = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                        nodeElevation += bEle / 2
                        self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                        self.elevationGrid[nodeNum] = nodeElevation
                        if wScoreRatio < -1.75 - erosionFactor * 0.15:
                            designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Dry"), k=1)[0]
                            if "SelfBonus" in self.terrainTypes.get(designatedTerrain):
                                bEle = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                            else:
                                bEle = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                            nodeElevation += bEle / 2
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.terrainRecord[designatedTerrain].add(nodeNum)
                        if designatedTerrain in self.terrainTypesWAT:
                            waterNodes.add(nodeNum)

            print('-Coastal Conversion Complete')

        elevationBasePoints = dict()
        elevatedAssociation = dict()
        altPoint = dict()
        colorCombos = []
        if self.stageModifier > 4:
            print('Begining Continent Organization...')

            # Note, this section down to the begining of the while loop is where all the slowdown is
            accurateContinents = False
            if accurateContinents:
                for nodeNum in self.nodeTerrainData:
                    nodeInfo = self.nodeTerrainData.get(nodeNum)
                    if nodeInfo.get("ChosenTerrain") in self.terrainTypesELE or nodeInfo.get("Elevation") > 12:
                        elevationBasePoints[nodeNum] = {"Elevated": [nodeNum], "Nodes": [nodeNum]}
                        elevatedAssociation[nodeNum] = [nodeNum]
            else:
                for terrainType in self.terrainTypesELE:
                    if terrainType in self.terrainRecord:
                        for nodeNum in self.terrainRecord.get(terrainType):
                            elevationBasePoints[nodeNum] = {"Elevated": [nodeNum], "Nodes": [nodeNum]}
                            elevatedAssociation[nodeNum] = [nodeNum]
            if not self.multiThreading:
                for nodeNum in self.nodeTerrainData:
                    if nodeNum not in elevationBasePoints:
                        minDist, minNode = float('inf'), None
                        nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                        if nodeX > self.columns - 8:
                            nodeX = (nodeX + 8) % self.columns
                        elif nodeX < 8:
                            nodeX = (nodeX - 8) % self.columns

                        if nodeY > self.rows - 8:
                            nodeY = (nodeY + 8) % self.rows
                        elif nodeX < 8:
                            nodeY = (nodeY - 8) % self.rows

                        proxyNodeNum = nodeY * self.columns + nodeX
                        altPoint[nodeNum] = proxyNodeNum
                        for basePoint in elevationBasePoints:
                            dist = distToSplit(nodeNum, basePoint)
                            if proxyNodeNum != nodeNum:
                                dist = min(distToSplit(proxyNodeNum, basePoint), dist)
                            if minNode is None:
                                minDist = dist
                                minNode = basePoint
                            else:
                                if dist < minDist:
                                    minDist = dist
                                    minNode = basePoint
                            if minDist <= 1:
                                break
                        elevationBasePoints[minNode]["Nodes"].append(nodeNum)
                        elevatedAssociation[minNode].append(nodeNum)
                    else:
                        nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                        if nodeX > self.columns - 8:
                            nodeX = (nodeX + 8) % self.columns
                        elif nodeX < 8:
                            nodeX = (nodeX - 8) % self.columns

                        if nodeY > self.rows - 8:
                            nodeY = (nodeY + 8) % self.rows
                        elif nodeX < 8:
                            nodeY = (nodeY - 8) % self.rows

                        proxyNodeNum = nodeY * self.columns + nodeX
                        altPoint[nodeNum] = proxyNodeNum
            else:
                runningThreads = []
                for nodeNum in self.nodeTerrainData:
                    newThread = customThread.mapAssociatedElevThread(nodeNum, self.nodeTerrainData, elevationBasePoints, self.columns, self.rows)
                    newThread.start()
                    runningThreads.append(newThread)
                for newThread in runningThreads:
                    newThread.join()
                    values = newThread.getVal()
                    elevationBasePoints[values[1]]["Nodes"].append(values[0])
                    elevatedAssociation[values[1]].append(values[0])
                    altPoint[values[0]] = values[2]

            # Generate Continents
            runAgain = True
            runningTime = 0
            while runAgain:
                print(f'Continent Organization #{runningTime}')
                runningTime += 1
                runAgain = False
                markedForChange = dict()
                markedSubCat = dict()
                for basePoint in elevationBasePoints:
                    if basePoint not in markedSubCat:
                        for basePoint2 in elevationBasePoints:
                            if basePoint != basePoint2:
                                dist = distToSplit(basePoint, basePoint2)
                                proxyNodeNum = altPoint.get(basePoint2)
                                if proxyNodeNum != basePoint2:
                                    dist = min(distToSplit(basePoint, basePoint2), dist)

                                for otherElevatedNode in elevationBasePoints.get(basePoint).get("Elevated"):
                                    if otherElevatedNode != basePoint:
                                        dist = min(distToSplit(otherElevatedNode, basePoint2), dist)
                                        proxyNodeNum2 = altPoint.get(otherElevatedNode)
                                        if proxyNodeNum2 != otherElevatedNode:
                                            try:
                                                dist = min(distToSplit(proxyNodeNum2, basePoint2), dist)
                                            except TypeError:
                                                print(proxyNodeNum2, otherElevatedNode)
                                                print(altPoint)
                                                raise Exception

                                # 16, 18, 19, 24
                                if dist <= 17:
                                    proceed = False
                                    if basePoint2 in markedSubCat:
                                        baseData = markedSubCat.get(basePoint2)
                                        if dist < baseData[1]:
                                            markedSubCat[basePoint2] = (basePoint, dist)
                                            markedForChange[baseData[0]].remove((baseData[0], basePoint2))
                                            if len(markedForChange.get(baseData[0])) < 1:
                                                del markedForChange[baseData[0]]
                                            proceed = True
                                    else:
                                        proceed = True
                                    if proceed:
                                        if markedForChange.get(basePoint) is None:
                                            markedForChange[basePoint] = []
                                        markedForChange[basePoint].append((basePoint, basePoint2))
                                        markedSubCat[basePoint2] = (basePoint, dist)

                if len(markedForChange) > 0:
                    for baseNode in markedForChange:
                        for baseNode1, baseNode2 in markedForChange.get(baseNode):
                            newArrN, newArrE, elligible = [], [], []
                            if elevationBasePoints.get(baseNode1) is not None:
                                elligible.append(baseNode1)
                                newArrN = elevationBasePoints.get(baseNode1).get("Nodes")
                                newArrE = elevationBasePoints.get(baseNode1).get("Elevated")
                            if elevationBasePoints.get(baseNode2) is not None:
                                elligible.append(baseNode2)
                                newArrN += elevationBasePoints.get(baseNode2).get("Nodes")
                                newArrE += elevationBasePoints.get(baseNode2).get("Elevated")
                            if len(elligible) > 1:
                                del elevationBasePoints[baseNode2]
                                elevationBasePoints[baseNode1]["Nodes"] = newArrN
                                elevationBasePoints[baseNode1]["Elevated"] = newArrE
                            else:
                                pass
                    runAgain = True

            colorCombos = []
            for continent in elevationBasePoints:
                redC, greenC, blueC = random.randint(0, 5) * 51, random.randint(0, 5) * 51, random.randint(0, 5) * 51
                while (redC, greenC, blueC) in colorCombos:
                    redC, greenC, blueC = random.randint(0, 5) * 51, random.randint(0, 5) * 51, random.randint(0, 5) * 51
                colorCombos.append((redC, greenC, blueC))

                # noinspection PyTypeChecker
                elevationBasePoints[continent]["Color"] = (redC, greenC, blueC)

                # noinspection PyTypeChecker
                elevationBasePoints[continent]["Name"] = "Placeholder"

                for nodeNum in elevationBasePoints.get(continent).get("Nodes"):
                    self.nodeTerrainData[nodeNum]["Continent"] = continent
            self.continentData = deepcopy(elevationBasePoints)

            print('-Continent Organization Complete')

        if self.stageModifier > 5:
            print('Begining Region Organization...')
            generateRegions = True
            if generateRegions:

                # Reuse data from continents, just reset arrays
                for nodeNum in elevationBasePoints:
                    elevationBasePoints[nodeNum] = {"Elevated": [nodeNum], "Nodes": [nodeNum]}

                # Now we run the while loop again, but with a distance of 16;
                # NOTE: This code is the exact same as above with only the distance modified
                totalRunningTime = 0
                continentRun = 0
                regionDataSave = dict()
                for continent in self.continentData:
                    print(f'-Working on Continent #{continentRun}')
                    continentRun += 1
                    runAgain = True
                    elevatedNodesToUse = self.continentData.get(continent).get("Elevated")
                    elevatedNodesLeft = list(range(0, len(elevatedNodesToUse) - 1))
                    regionDataSave[continent] = dict()
                    regionRun = 0
                    regionFlagger = False

                    if len(elevatedNodesToUse) == 1:
                        regionDataSave[continent][elevatedNodesToUse[0]] = [elevatedNodesToUse[0]]
                    else:
                        while runAgain or regionFlagger:
                            runAgain = False
                            regionRun += 1
                            while elevatedNodesLeft:
                                randIndex = elevatedNodesLeft[random.randint(0, len(elevatedNodesLeft) - 1)]
                                randNode = elevatedNodesToUse[randIndex]
                                elevatedNodesLeft.remove(randIndex)
                                markedForChange = []
                                for regionElevatedNode in elevatedNodesToUse:
                                    if regionElevatedNode != randNode:
                                        dist = distToSplit(randNode, regionElevatedNode)
                                        proxyNodeNum = altPoint.get(regionElevatedNode)
                                        if proxyNodeNum != regionElevatedNode:
                                            dist = min(distToSplit(randNode, regionElevatedNode), dist)
                                        if dist <= 17:
                                            markedForChange.append(regionElevatedNode)
                                        else:
                                            if randNode in regionDataSave.get(continent):
                                                for entry in regionDataSave.get(continent).get(randNode):
                                                    dist = distToSplit(entry, regionElevatedNode)
                                                    proxyNodeNum2 = altPoint.get(entry)
                                                    if proxyNodeNum2 != entry:
                                                        dist = min(distToSplit(proxyNodeNum2, regionElevatedNode), dist)
                                                    if dist <= 17:
                                                        markedForChange.append(regionElevatedNode)
                                                        break
                                if len(markedForChange) > 0:
                                    runAgain = True
                                    if randNode not in regionDataSave.get(continent):
                                        regionDataSave[continent][randNode] = [randNode]
                                    for entry in markedForChange:
                                        regionDataSave[continent][randNode].append(entry)
                                        if entry in regionDataSave.get(continent):
                                            regionDataSave[continent][randNode] += regionDataSave.get(continent).get(entry)
                                            del regionDataSave[continent][entry]
                                else:
                                    if not regionFlagger:
                                        regionFlagger = True
                                    else:
                                        regionFlagger = False
                                        break

                    # print(f'--Finished Continent #{continentRun}')

                regionDataSaveNew = dict()
                for continent in regionDataSave:
                    baseColor = self.continentData.get(continent).get("Color")
                    for region in regionDataSave.get(continent):
                        maxTries, currentAttempt = 35, 0
                        redC, greenC, blueC = max(min(random.randint(-3, 3) * 15 + baseColor[0], 255), 0), max(min(random.randint(-3, 3) * 15 + baseColor[1], 255), 0), max(min(random.randint(-3, 3) * 15 + baseColor[2], 255), 0)
                        while (redC, greenC, blueC) in colorCombos and currentAttempt < maxTries:
                            currentAttempt += 1
                            redC, greenC, blueC = max(min(random.randint(-3, 3) * 15 + baseColor[0], 255), 0), max(min(random.randint(-3, 3) * 15 + baseColor[1], 255), 0), max(min(random.randint(-3, 3) * 15 + baseColor[2], 255), 0)
                        colorCombos.append((redC, greenC, blueC))
                        regionDataSaveNew[region] = dict()
                        regionDataSaveNew[region]["Color"] = (redC, greenC, blueC)
                        regionDataSaveNew[region]["Name"] = "Placeholder"
                        regionDataSaveNew[region]["Elevated"] = regionDataSave.get(continent).get(region)
                        for elevatedNode in regionDataSave.get(continent).get(region):
                            for nodeNum in elevatedAssociation.get(elevatedNode):
                                self.nodeTerrainData[nodeNum]["Region"] = region
                self.regionData = regionDataSaveNew

            print('-Region Organization Complete')

        if self.stageModifier > 6:
            print('Begining River Generation...')
            for region in self.regionData:

                numRivers = random.randint(0, 4)
                self.riverDict[region] = dict()
                for river in range(0, numRivers):
                    riverStartNode = self.regionData.get(region).get("Elevated")
                    riverStartNode = random.choices(riverStartNode, k=1)[0]
                    regionSearch = True
                    currentNode = riverStartNode
                    riverNodes = set()
                    riverNodes.add(riverStartNode)
                    maxRiverLength = 16
                    while regionSearch:
                        currentNX = currentNode % self.columns
                        currentNY = currentNode // self.columns
                        currentNodeEle = self.nodeTerrainData.get(currentNode).get("Elevation")
                        adjacentNodes = []
                        elevationArr = []
                        for pRow in range(currentNY - 1, currentNY + 1 + 1):
                            row = pRow % self.rows
                            for pColumn in range(currentNX - 1, currentNX + 1 + 1):
                                column = pColumn % self.columns
                                nodeNum = row * self.columns + column
                                elevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                                if elevation < currentNodeEle * 1.30 and nodeNum not in riverNodes:
                                    adjacentNodes.append(nodeNum)
                                    elevation = 100/pow(pow(math.e, elevation), 2)
                                    elevationArr.append(elevation)

                        if len(adjacentNodes) < 1 or len(riverNodes) > maxRiverLength:
                            regionSearch = False
                        else:
                            currentNode = random.choices(adjacentNodes, elevationArr, k=1)[0]
                            riverNodes.add(currentNode)

                            if currentNode in waterNodes:
                                regionSearch = False
                    for nodeNum in riverNodes:
                        self.nodeTerrainData[nodeNum]["River"] = riverStartNode

                    lenORiver = len(riverNodes)
                    for fork in range(0, lenORiver // 6):
                        currentNode = random.choices(list(riverNodes), k=1)[0]
                        maxRiverLength = fork*4
                        regionSearch = True
                        while regionSearch:
                            currentNX = currentNode % self.columns
                            currentNY = currentNode // self.columns
                            currentNodeEle = self.nodeTerrainData.get(currentNode).get("Elevation")
                            adjacentNodes = []
                            elevationArr = []
                            for pRow in range(currentNY - 1, currentNY + 1 + 1):
                                row = pRow % self.rows
                                for pColumn in range(currentNX - 1, currentNX + 1 + 1):
                                    column = pColumn % self.columns
                                    nodeNum = row * self.columns + column
                                    elevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                                    if elevation < currentNodeEle * 1.30 and nodeNum not in riverNodes:
                                        adjacentNodes.append(nodeNum)
                                        elevation = 100 / pow(pow(math.e, elevation), 2)
                                        elevationArr.append(elevation)

                            if len(adjacentNodes) < 1 or len(riverNodes) > maxRiverLength + lenORiver:
                                regionSearch = False
                            else:
                                currentNode = random.choices(adjacentNodes, elevationArr, k=1)[0]
                                riverNodes.add(currentNode)

                                if currentNode in waterNodes:
                                    regionSearch = False
                        for nodeNum in riverNodes:
                            self.nodeTerrainData[nodeNum]["River"] = riverStartNode

                    riverDict = {
                        "Nodes": riverNodes,
                        "Start": riverStartNode,
                        "End": currentNode
                    }
                    self.riverDict[region][riverStartNode] = riverDict

            print('-River Generation Complete')

            print('Begining River Spread')
            for region in self.riverDict:
                for river in self.riverDict.get(region):
                    riverNodes = self.riverDict.get(region).get(river).get("Nodes")
                    for nodeNum in riverNodes:
                        designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]

                        ranNum = random.randint(0, 100)
                        if ranNum > 65 - 2 * len(riverNodes):
                            designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]

                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.nodeTerrainData[nodeNum]["WaterScore"] += self.terrainTypes.get(designatedTerrain).get("WaterScore")
                        bEle = self.terrainTypes.get(designatedTerrain).get("EffectBonus")
                        if "SelfBonus" in self.terrainTypes.get(designatedTerrain):
                            bEle = self.terrainTypes.get(designatedTerrain).get("SelfBonus")
                        self.nodeTerrainData[nodeNum]["Elevation"] += bEle / 2
                        self.elevationGrid[nodeNum] += bEle / 2
                        if designatedTerrain not in self.terrainRecord:
                            self.terrainRecord[designatedTerrain] = set()
                        self.terrainRecord[designatedTerrain].add(nodeNum)

            print('-River Spread Complete')


        print('Initiating Nodes...')
        nodeDict = dict()
        for nodeNum in self.nodeTerrainData:
            nodeDict[nodeNum] = node.Node(nodeNum, self.gameObj)
        self.nodeTerrainData = nodeDict

        print(f'We finished map generation-- this took {time.time() - startTime} seconds')


    def getAdjustFactor(self):
        return self.adjustFactor

    def getTerrainTypes(self):
        return self.terrainTypes

    def getTerrainData(self):
        return self.nodeTerrainData

    def getContinentData(self):
        return self.continentData

    def getRiverData(self):
        return self.riverDict

    def getRegionData(self):
        return self.regionData

    def fetchStageModifier(self):
        return self.stageModifier

    def advanceStageModifier(self):
        # NOTE-- this will result in regenerating the map
        self.stageModifier += 1

    def getWaterTerrainTypes(self):
        return self.terrainTypesWAT

    def getRows(self):
        return self.rows

    def getColumns(self):
        return self.columns
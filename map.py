import random
import time
import pygame

import customThread


# noinspection PyPep8Naming
class Map:
    def __init__(self):
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

        # NOTE: Currently multithreading is VERY Ineffective, taking around ~44 times longer with blocky terrain following the lattitude bands
        self.multiThreading = False

        self.columns, self.rows = 1024 // self.adjustFactor, 576 // self.adjustFactor
        # self.columns, self.rows = 256, 144
        # self.columns, self.rows = 32, 18
        pygame.init()
        self.elevationGrid = dict()

        # Seed must have all 0-9 numbers, and be within 24 digits

        seed = 544786120398304714620491
        random.seed(seed)
        # random.seed(time.time())

        # self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor+self.adjustFactor*8))

        self.terrainTypes = {
            "Ocean": {
                "RegionSelChance": 0,
                "NodeSelChance": 0,
                "Diffusion": 0,
                "Color": (0, 0, 60),
                "PTQ": (-1, -1),
                "HPTQ": (-1, -1),
                "Wet": "Ice",
                "Dry": "Plains",
                "EffectBonus": 0,
                "WaterScore": 2
            },
            "Coastal": {
                "RegionSelChance": 0,
                "NodeSelChance": 0,
                "Diffusion": 0,
                "Color": (0, 0, 120),
                "PTQ": (-1, -1),
                "HPTQ": (-1, -1),
                "Wet": "Ice",
                "Dry": "Plains",
                "EffectBonus": 0,
                "WaterScore": 1
            },
            "Ice": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.05,
                "Color": (255, 255, 255),
                "PTQ": (0, 25),
                "HPTQ": (0, 28),
                "Wet": "Ocean",
                "Dry": "Coastal",
                "EffectBonus": -2,
                "WaterScore": 0.5
            },
            "Tundra": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (230, 230, 230),
                "PTQ": (23, 35),
                "HPTQ": (15, 55),
                "Wet": "Taiga",
                "Dry": "Tundra",
                "EffectBonus": -1,
                "WaterScore": 0
            },
            "Taiga": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.25,
                "Color": (160, 180, 160),
                "PTQ": (25, 35),
                "HPTQ": (17, 59),
                "Wet": "Taiga",
                "Dry": "Tundra",
                "EffectBonus": 0,
                "WaterScore": 0.25
            },
            "Forest": {
                "RegionSelChance": 20,
                "NodeSelChance": 20,
                "Diffusion": 0.25,
                "Color": (0, 60, 0),
                "PTQ": (44, 63),
                "HPTQ": (34, 85),
                "Wet": "Forest",
                "Dry": "Grassland",
                "EffectBonus": 2,
                "WaterScore": 0
            },
            "Grassland": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.10,
                "Color": (70, 200, 50),
                "PTQ": (43, 68),
                "HPTQ": (33, 86),
                "Wet": "Forest",
                "Dry": "Plains",
                "EffectBonus": 1,
                "WaterScore": 0
            },
            "Plains": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (150, 200, 50),
                "PTQ": (65, 85),
                "HPTQ": (55, 90),
                "Wet": "Grassland",
                "Dry": "Desert",
                "EffectBonus": 0,
                "WaterScore": 0
            },
            "Desert": {
                "RegionSelChance": 20,
                "NodeSelChance": 25,
                "Diffusion": -0.05,
                "Color": (220, 190, 50),
                "PTQ": (80, 100),
                "HPTQ": (75, 100),
                "Wet": "Oasis",
                "Dry": "Desert",
                "EffectBonus": 0,
                "WaterScore": -1
            },
            "Oasis": {
                "RegionSelChance": 20,
                "NodeSelChance": 0.25,
                "Diffusion": -0.05,
                "Color": (30, 175, 140),
                "PTQ": (90, 100),
                "HPTQ": (80, 100),
                "Wet": "Plains",
                "Dry": "Desert",
                "EffectBonus": 0,
                "WaterScore": 0.5
            },
            "Hills": {
                "RegionSelChance": 20,
                "NodeSelChance": 5,
                "Diffusion": -0.10,
                "Color": (170, 150, 50),
                "PTQ": (35, 95),
                "HPTQ": (33, 100),
                "Wet": "Hills",
                "Dry": "Hills",
                "RangeBonus": 3,
                "EffectBonus": 5,
                "SelfBonus": 4,
                "WaterScore": -1.5
            },
            "Mountains": {
                "RegionSelChance": 30,
                "NodeSelChance": 1,
                "Diffusion": -0.15,
                "Color": (50, 50, 70),
                "PTQ": (35, 85),
                "HPTQ": (30, 95),
                "Wet": "Mountains",
                "Dry": "Mountains",
                "RangeBonus": 5,
                "EffectBonus": 8,
                "SelfBonus": 5,
                "WaterScore": -3
            }
        }
        self.terrainTypesELE = ["Mountains", "Hills"]
        self.terrainTypesWAT = ["Ocean, Coastal, Oasis"]

        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = []
        self.nodeTerrainData = dict()

        startTime = time.time()
        print('Begining generation...')
        self.generateMap()
        print(f'We finished map generation-- this took {time.time()-startTime} seconds')

    def generateMap(self):

        def distToSplit(nodeNum1, nodeNum2):
            nodeNum1x, nodeNum1y = nodeNum1 % self.columns, int(nodeNum1 / self.columns)
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        def distToGiven(nodeNum1x, nodeNum1y, nodeNum2x, nodeNum2y):
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        instancedNodes = dict()

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

        print('Begining Diffusion...')
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
                                    # Fetch our distance from the center of the range
                                    temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 50
                                    diffuseWeight = max(diffuseWeight - pow(temp, 1.1), 1)
                                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                                    # Fetch our distance from the center of the range
                                    temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 50
                                    diffuseWeight = max(diffuseWeight - pow(temp, 2.5), 1)
                                else:
                                    temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 50
                                    diffuseWeight = 0.25 * max(diffuseWeight - pow(temp, 3.25), 1)
                                    # diffuseWeight *= 0.25
                                diffuseWeight = diffuseWeight / pow(distToDiffuseNode-0.75, 0.7)

                                if diffuseTerrain not in self.nodeTerrainData.get(nodeNum).get("Weights"):
                                    self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = diffuseWeight
                                else:
                                    self.nodeTerrainData[nodeNum]["Weights"][diffuseTerrain] = pow(pow(diffuseWeight, 2) + pow(self.nodeTerrainData.get(nodeNum).get("Weights").get(diffuseTerrain), 2), 0.5)

            # Currently, multithreading is slower than doing it manually, this may be due to unoptimized code
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
                self.terrainRecord[designatedTerrain].append(nodeNum)
                instancedNodes[nodeNum] = True
            except ValueError:
                print(proxyTArr)
                print(proxyWeightArr)
                print(self.nodeTerrainData.get(nodeNum))
                print(len(instancedNodes))
                raise Exception

        print('-Diffusion Complete')

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
            self.elevationGrid[nodeNum] = random.randint(selfBonus - 2, selfBonus + 3) + effectBonus
            nodeElevation = self.elevationGrid.get(nodeNum)
            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation

            for cY in range(max(nodeY - rangeBonus * 2 - random.randint(0, 1), 0), min(nodeY + rangeBonus * 2 + random.randint(0, 1), self.rows)):
                for cX in range(max(nodeX - rangeBonus * 2 - random.randint(0, 1), 0), min(nodeX + rangeBonus * 2 + random.randint(0, 1), self.columns)):
                    diffuseNodeNum = cY * self.columns + cX
                    if diffuseNodeNum not in elevatedNodes:
                        distToDiffuseNode = distToGiven(nodeX, nodeY, cX, cY)
                        if distToDiffuseNode < rangeBonus * 2.9:
                            diffuseElevation = nodeElevation/pow(distToDiffuseNode, 0.7) - effectBonus/rangeBonus
                            designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                            effectBonus = int(self.terrainTypes.get(designatedTerrain).get("EffectBonus") * 0.5)
                            diffuseElevation += random.randint(-3 + effectBonus, 1 + effectBonus)

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
                    self.elevationGrid[nodeNum] = random.randint(-3 + effectBonus, 1 + effectBonus)
                    self.nodeTerrainData[nodeNum]["Elevation"] = self.elevationGrid.get(nodeNum)
                else:
                    nodeElevation = sorted(self.nodeTerrainData.get(nodeNum).get("Elevation"))
                    if len(nodeElevation) > 1:
                        self.nodeTerrainData[nodeNum]["Elevation"] = sum(nodeElevation)/len(nodeElevation) + nodeElevation[-1]/(len(nodeElevation)-1)
                    else:
                        self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation[0]
                    self.elevationGrid[nodeNum] = self.nodeTerrainData.get(nodeNum).get("Elevation")
        print('-ElevationMap Complete')

        print('Begining Coastal Conversion w/ Elevation')
        waterNodes = []
        for terrainType in self.terrainTypesWAT:
            if terrainType in self.terrainRecord:
                for nodeNum in self.terrainRecord.get(terrainType):
                    waterNodes.append(nodeNum)

        for nodeNum in self.nodeTerrainData:
            designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
            nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
            if nodeElevation < -3:
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                self.terrainRecord[designatedTerrain].remove(nodeNum)
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                self.terrainRecord["Ocean"].append(nodeNum)
                waterNodes.append(nodeNum)
            elif nodeElevation < 1:
                self.terrainRecord[designatedTerrain].remove(nodeNum)
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Coastal"
                self.terrainRecord["Coastal"].append(nodeNum)
                waterNodes.append(nodeNum)
            elif nodeElevation < 1.5:
                self.terrainRecord[designatedTerrain].remove(nodeNum)
                designatedTerrain = self.terrainTypes.get(designatedTerrain).get("Wet")
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                self.terrainRecord[designatedTerrain].append(nodeNum)
            elif nodeElevation > 10:
                self.terrainRecord[designatedTerrain].remove(nodeNum)
                designatedTerrain = self.terrainTypes.get(designatedTerrain).get("Dry")
                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                self.terrainRecord[designatedTerrain].append(nodeNum)

        print('Begining Coastal Conversion w/ Proximity')

        for nodeNum in self.nodeTerrainData:
            designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
            nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
            # if designatedTerrain not in self.terrainTypesWAT and nodeElevation < 5:
            if nodeNum not in waterNodes and nodeElevation < 5:
                nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                breakedOutOfLoop = False
                waterScore = 0
                numScoreNodes = 0
                for cY in range(max(nodeY - 2, 0), min(nodeY + 2, self.rows)):
                    for cX in range(max(nodeX - 2, 0), min(nodeX + 2, self.columns)):
                        diffuseNodeNum = cY * self.columns + cX
                        # diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                        numScoreNodes += 1
                        # if diffuseTerrain in self.terrainTypesWAT:
                        if diffuseNodeNum in waterNodes:
                            diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                            waterScore += self.terrainTypes.get(diffuseTerrain).get("WaterScore")

                            if not breakedOutOfLoop:
                                self.terrainRecord[designatedTerrain].remove(nodeNum)
                                designatedTerrain = self.terrainTypes.get(designatedTerrain).get("Wet")
                                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                                self.terrainRecord[designatedTerrain].append(nodeNum)
                                breakedOutOfLoop = True
                if waterScore / numScoreNodes > 0.55:
                    if waterScore > 0.95:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                        self.terrainRecord["Ocean"].append(nodeNum)
                        nodeElevation = nodeElevation - self.terrainTypes.get("Ocean").get("WaterScore") * 2
                        self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                        self.elevationGrid[nodeNum] = nodeElevation
                    else:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Coastal"
                        self.terrainRecord["Coastal"].append(nodeNum)
                        nodeElevation = nodeElevation - self.terrainTypes.get("Ocean").get("WaterScore") * 2
                        self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                        self.elevationGrid[nodeNum] = nodeElevation

        print('-Coastal Conversion Complete')

        print('Begining Continent Organization')

        elevationBasePoints = dict()
        for terrainType in self.terrainTypesELE:
            if terrainType in self.terrainRecord:
                for nodeNum in self.terrainRecord.get(terrainType):
                    elevationBasePoints[nodeNum] = []

        for nodeNum in self.nodeTerrainData:
            if nodeNum not in elevationBasePoints:
                minDist, minNode = float('inf'), float('inf')
                for basePoint in elevationBasePoints:
                    dist = distToSplit(nodeNum, basePoint)
                    if dist < minDist:
                        minDist = dist
                        minNode = basePoint
                        if minDist < 3:
                            break
                elevationBasePoints[minNode].append(nodeNum)

        runAgain = True
        while runAgain:
            runAgain = False
            markedForChange = []
            for basePoint in elevationBasePoints:
                if basePoint not in markedForChange:
                    for basePoint2 in elevationBasePoints:
                        if basePoint != basePoint2 and basePoint2 not in markedForChange:
                            dist = distToSplit(basePoint, basePoint2)
                            designatedTerrain = self.nodeTerrainData.get(basePoint).get("ChosenTerrain")
                            if dist <= self.terrainTypes.get(designatedTerrain).get("RangeBonus"):
                                markedForChange.append((basePoint, basePoint2))

            if len(markedForChange) > 0:
                for baseNode1, baseNode2 in markedForChange:
                    newArr, elligible = [], []
                    if elevationBasePoints.get(baseNode1) is not None:
                        elligible.append(baseNode1)
                        for nodeNum in elevationBasePoints.get(baseNode1):
                            newArr.append(nodeNum)
                    if elevationBasePoints.get(baseNode2) is not None:
                        elligible.append(baseNode2)
                        for nodeNum in elevationBasePoints.get(baseNode2):
                            newArr.append(nodeNum)
                    if len(elligible) > 1:
                        del elevationBasePoints[baseNode2]
                        elevationBasePoints[baseNode1] = newArr
                    else: pass
                runAgain = True

        print('-Continent Organization Complete')

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

    def getAdjustFactor(self):
        return self.adjustFactor

    def getTerrainTypes(self):
        return self.terrainTypes

    def getTerrainData(self):
        return self.nodeTerrainData

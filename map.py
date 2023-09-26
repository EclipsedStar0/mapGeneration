import math
import random
import time
from copy import deepcopy

import pygame

import customThread


# noinspection PyPep8Naming
class Map:
    def __init__(self, stageModifier=7, seedPara=None):
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

        self.terrainTypes = {
            "Ocean": {
                "RegionSelChance": 0,
                "NodeSelChance": 0,
                "Diffusion": 0,
                "Color": (0, 0, 60),
                "PTQ": (-1, -1),
                "HPTQ": (-1, -1),
                "Wet": ["Ocean"],
                "Dry": ["Coastal", "Coastal", "Coastal", "Ice"],
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
                "Wet": ["Coastal", "Coastal", "Ocean"],
                "Dry": ["Ice"],
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
                "Wet": ["Coastal", "Coastal", "Coastal", "Ocean"],
                "Dry": ["Tundra", "Coastal"],
                "EffectBonus": -4,
                "WaterScore": 0.5,
                "Similar": ["Tundra, Taiga"]
            },
            "Tundra": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (230, 230, 230),
                "PTQ": (23, 35),
                "HPTQ": (15, 55),
                "Wet": ["Taiga", "Taiga", "Ice"],
                "Dry": ["Tundra"],
                "EffectBonus": -1,
                "WaterScore": 0,
                "Similar": ["Taiga"]
            },
            "Taiga": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.25,
                "Color": (160, 180, 160),
                "PTQ": (25, 35),
                "HPTQ": (17, 59),
                "Wet": ["Taiga"],
                "Dry": ["Tundra", "Tundra", "Tundra", "Tundra", "Forest"],
                "EffectBonus": 0,
                "WaterScore": 0.25
            },
            "Forest": {
                "RegionSelChance": 20,
                "NodeSelChance": 20,
                "Diffusion": 0.35,
                "Color": (0, 60, 0),
                "PTQ": (44, 63),
                "HPTQ": (34, 85),
                "Wet": ["Forest"],
                "Dry": ["Grassland", "Grassland", "Plains"],
                "EffectBonus": 2,
                "WaterScore": 0,
                "Similar": ["Grassland"]
            },
            "Grassland": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.10,
                "Color": (70, 200, 50),
                "PTQ": (43, 68),
                "HPTQ": (33, 86),
                "Wet": ["Grassland", "Forest", "Forest"],
                "Dry": ["Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Savannah"],
                "EffectBonus": 1,
                "WaterScore": 0,
                "Similar": ["Forest", "Plains"]
            },
            "Plains": {
                "RegionSelChance": 20,
                "NodeSelChance": 35,
                "Diffusion": 0.05,
                "Color": (150, 200, 50),
                "PTQ": (70, 85),
                "HPTQ": (60, 87),
                "Wet": ["Grassland"],
                "Dry": ["Desert", "Desert", "Desert", "Desert", "Savannah"],
                "EffectBonus": 0,
                "WaterScore": 0,
                "Similar": ["Grassland", "Savannah"]
            },
            "Savannah": {
                "RegionSelChance": 10,
                "NodeSelChance": 2,
                "Diffusion": -0.3,
                "Color": (170, 130, 80),
                "PTQ": (75, 90),
                "HPTQ": (65, 95),
                "Wet": ["Plains", "Plains", "Plains", "Plains", "Savannah", "Oasis"],
                "Dry": ["Desert"],
                "EffectBonus": 0,
                "WaterScore": -0.25,
                "Similar": ["Savannah", "Oasis"]
            },
            "Desert": {
                "RegionSelChance": 20,
                "NodeSelChance": 25,
                "Diffusion": -0.05,
                "Color": (220, 190, 50),
                "PTQ": (80, 100),
                "HPTQ": (75, 100),
                "Wet": ["Savannah", "Oasis", "Oasis", "Oasis", "Oasis", "Oasis", "Oasis", "Oasis"],
                "Dry": ["Desert"],
                "EffectBonus": 0,
                "WaterScore": -1,
                "Similar": ["Savannah", "Oasis"]
            },
            "Oasis": {
                "RegionSelChance": 20,
                "NodeSelChance": 0.25,
                "Diffusion": -0.05,
                "Color": (30, 175, 140),
                "PTQ": (90, 100),
                "HPTQ": (80, 100),
                "Wet": ["Oasis"],
                "Dry": ["Desert", "Desert", "Desert", "Desert", "Savannah"],
                "EffectBonus": 0,
                "WaterScore": 0.5,
                "Similar": ["Desert"]
            },
            "Steppe": {
                "RegionSelChance": 20,
                "NodeSelChance": 2,
                "Diffusion": -0.25,
                "Color": (150, 150, 120),
                "PTQ": (65, 95),
                "HPTQ": (43, 100),
                "Wet": ["Steppe"],
                "Dry": ["Steppe"],
                "RangeBonus": 2,
                "EffectBonus": 4,
                "SelfBonus": 2,
                "WaterScore": -0.5,
                "Similar": ["Steppe", "Mountains"]
            },
            "Hills": {
                "RegionSelChance": 20,
                "NodeSelChance": 5,
                "Diffusion": -0.10,
                "Color": (170, 150, 50),
                "PTQ": (35, 95),
                "HPTQ": (33, 100),
                "Wet": ["Hills"],
                "Dry": ["Hills"],
                "RangeBonus": 3,
                "EffectBonus": 5,
                "SelfBonus": 4,
                "WaterScore": -1.5,
                "Similar": ["Steppe", "Mountains"]
            },
            "Mountains": {
                "RegionSelChance": 30,
                "NodeSelChance": 1,
                "Diffusion": -0.15,
                "Color": (50, 50, 70),
                "PTQ": (35, 85),
                "HPTQ": (30, 95),
                "Wet": ["Mountains"],
                "Dry": ["Mountains"],
                "RangeBonus": 5,
                "EffectBonus": 8,
                "SelfBonus": 5,
                "WaterScore": -3,
                "Similar": ["Hills"]
            }
        }
        self.terrainTypesELE = ["Mountains", "Hills", "Steppe"]
        self.terrainTypesWAT = ["Ocean, Coastal, Oasis"]

        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = []
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

        startTime = time.time()
        print('Begining generation...')
        self.generateMap()
        print(f'We finished map generation-- this took {time.time() - startTime} seconds')

    def generateMap(self):

        # NOTE-- we are redefining these here incase we regenerate the map in the GUI to advance a stage
        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = []
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
            else:
                for column in range(0, self.columns):
                    nodeNum = row * self.columns + column
                    self.nodeTerrainData[nodeNum] = dict()
                    self.nodeTerrainData[nodeNum]["Weights"] = terrainWeightArr
                '''randomChance = random.randint(0, 100)
                if randomChance > 85:
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
                        self.terrainRecord[designatedTerrain] = []
                    self.terrainRecord[designatedTerrain].append(nodeNum)
                    instancedNodes[nodeNum] = True'''

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

                for cY in range(max(nodeY - self.radialSearch, 0), min(nodeY + self.radialSearch + 1, self.rows)):
                    for cX in range(max(nodeX - self.radialSearch, 0), min(nodeX + self.radialSearch + 1, self.columns)):
                        diffuseNodeNum = cY * self.columns + cX
                        if diffuseNodeNum in instancedNodes and diffuseNodeNum != nodeNum:
                            # This thread is very ineffective
                            if self.multiThreading and False:
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
                                    diffusionVal = self.terrainTypes.get(diffuseTerrain).get("Diffusion")
                                    if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                                        # Fetch our distance from the center of the range
                                        temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 50
                                        diffuseWeight = max(diffuseWeight - pow(temp, 1.1-diffusionVal), 0)
                                    elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                                        # Fetch our distance from the center of the range
                                        temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                                        diffuseWeight = max(diffuseWeight - pow(temp, 2.5-diffusionVal), 0)
                                    else:
                                        temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                                        diffuseWeight = 0.25 * max(diffuseWeight - pow(temp, 3.25-diffusionVal), 0)
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
                    self.terrainRecord[designatedTerrain].append(nodeNum)
                    instancedNodes[nodeNum] = True
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
                self.elevationGrid[nodeNum] = random.randint(selfBonus - 2, selfBonus + 3) + effectBonus
                nodeElevation = self.elevationGrid.get(nodeNum)
                self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation

                for cY in range(max(nodeY - rangeBonus * 2 - random.randint(0, 1), 0), min(nodeY + rangeBonus * 2 + random.randint(0, 1) + 1, self.rows)):
                    for cX in range(max(nodeX - rangeBonus * 2 - random.randint(0, 1), 0), min(nodeX + rangeBonus * 2 + random.randint(0, 1) + 1, self.columns)):
                        diffuseNodeNum = cY * self.columns + cX
                        if diffuseNodeNum not in elevatedNodes:
                            distToDiffuseNode = distToGiven(nodeX, nodeY, cX, cY)
                            if distToDiffuseNode < rangeBonus * 2.9:
                                diffuseElevation = nodeElevation / pow(distToDiffuseNode, 0.7) - effectBonus / rangeBonus
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
                            self.nodeTerrainData[nodeNum]["Elevation"] = sum(nodeElevation) / len(nodeElevation) + nodeElevation[-1] / (len(nodeElevation) - 1)
                        else:
                            ranEle = random.randint(-1, 3)
                            self.nodeTerrainData[nodeNum]["Elevation"] = (nodeElevation[0] + ranEle) / 2 + ranEle / (2-1)
                        self.elevationGrid[nodeNum] = self.nodeTerrainData.get(nodeNum).get("Elevation")
            print('-ElevationMap Complete')

        waterNodes = []
        if self.stageModifier > 2:
            print('Begining Coastal Conversion w/ Elevation')
            for terrainType in self.terrainTypesWAT:
                if terrainType in self.terrainRecord:
                    for nodeNum in self.terrainRecord.get(terrainType):
                        waterNodes.append(nodeNum)

            '''Currently, default approach is faster than multithreading'''
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
                    if values[0] != values[1]:
                        self.terrainRecord[values[1]].remove(values[2])
                        self.nodeTerrainData[values[2]]["ChosenTerrain"] = values[0]
                        self.terrainRecord[values[0]].append(values[2])
                        if values[0] == "Ocean" or values[0] == "Coastal":
                            waterNodes.append(values[2])
            else:
                for nodeNum in self.nodeTerrainData:
                    designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    if nodeElevation < -4:
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                        self.terrainRecord["Ocean"].append(nodeNum)
                        waterNodes.append(nodeNum)
                    elif nodeElevation < 1.5:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Coastal"
                        self.terrainRecord["Coastal"].append(nodeNum)
                        waterNodes.append(nodeNum)
                    elif nodeElevation < 5:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.terrainRecord[designatedTerrain].append(nodeNum)
                        if designatedTerrain in self.terrainTypesWAT:
                            waterNodes.append(nodeNum)
                    elif nodeElevation > 10:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Dry"), k=1)[0]
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.terrainRecord[designatedTerrain].append(nodeNum)

        if self.stageModifier > 3:
            print('Begining Coastal Conversion w/ Proximity')

            ranNodesToCheck = []
            erosionFactor, erosionOverride = 1, 12
            for errosionInterval in range(erosionFactor):
                print(f'-Initiating Erosion Stage #{errosionInterval+1}')
                for nodeNum in self.nodeTerrainData:
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    # if designatedTerrain not in self.terrainTypesWAT and nodeElevation < 5:
                    if nodeNum not in waterNodes and nodeElevation < max(7 * erosionFactor, erosionOverride):
                        ranNodesToCheck.append(nodeNum)

                while len(ranNodesToCheck) > 0:
                    nodeNumIndex = random.randint(0, len(ranNodesToCheck)-1)
                    nodeNum = ranNodesToCheck[nodeNumIndex]
                    del ranNodesToCheck[nodeNumIndex]

                    designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                    nodeElevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                    nodeX, nodeY = nodeNum % self.columns, nodeNum // self.columns
                    # breakedOutOfLoop = False
                    waterScore = 0
                    numScoreNodes = 0
                    coastalSearchRange = 1
                    for cY in range(max(nodeY - coastalSearchRange, 0), min(nodeY + coastalSearchRange + 1, self.rows)):
                        for cX in range(max(nodeX - coastalSearchRange, 0), min(nodeX + coastalSearchRange + 1, self.columns)):
                            diffuseNodeNum = cY * self.columns + cX
                            # diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                            numScoreNodes += 1
                            # if diffuseTerrain in self.terrainTypesWAT:
                            # if diffuseNodeNum in waterNodes:

                            diffuseTerrain = self.nodeTerrainData.get(diffuseNodeNum).get("ChosenTerrain")
                            waterScore += self.terrainTypes.get(diffuseTerrain).get("WaterScore")

                            '''if not breakedOutOfLoop:
                                self.terrainRecord[designatedTerrain].remove(nodeNum)
                                designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                                self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                                self.terrainRecord[designatedTerrain].append(nodeNum)
                                breakedOutOfLoop = True'''
                    if waterScore / numScoreNodes > 0.55:
                        if waterScore > 0.95:
                            self.terrainRecord[designatedTerrain].remove(nodeNum)
                            self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Ocean"
                            self.terrainRecord["Ocean"].append(nodeNum)
                            nodeElevation = nodeElevation - self.terrainTypes.get("Ocean").get("WaterScore") * 2
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                            waterNodes.append(nodeNum)
                        else:
                            self.terrainRecord[designatedTerrain].remove(nodeNum)
                            self.nodeTerrainData[nodeNum]["ChosenTerrain"] = "Coastal"
                            self.terrainRecord["Coastal"].append(nodeNum)
                            nodeElevation = nodeElevation - self.terrainTypes.get("Coastal").get("WaterScore") * 2
                            self.nodeTerrainData[nodeNum]["Elevation"] = nodeElevation
                            self.elevationGrid[nodeNum] = nodeElevation
                            waterNodes.append(nodeNum)
                    elif waterScore / numScoreNodes > 0.25:
                        self.terrainRecord[designatedTerrain].remove(nodeNum)
                        designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                        if waterScore / numScoreNodes > 0.40:
                            designatedTerrain = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                        self.nodeTerrainData[nodeNum]["ChosenTerrain"] = designatedTerrain
                        self.terrainRecord[designatedTerrain].append(nodeNum)
                        if designatedTerrain in self.terrainTypesWAT:
                            waterNodes.append(nodeNum)

            print('-Coastal Conversion Complete')

        elevationBasePoints = dict()
        elevatedAssociation = dict()
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
                        for basePoint in elevationBasePoints:
                            dist = distToSplit(nodeNum, basePoint)
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
                                for otherElevatedNode in elevationBasePoints.get(basePoint).get("Elevated"):
                                    if otherElevatedNode != basePoint:
                                        dist = min(distToSplit(otherElevatedNode, basePoint2), dist)
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
                            print(f'--Run #{regionRun}')
                            regionRun += 1
                            while elevatedNodesLeft:
                                randIndex = elevatedNodesLeft[random.randint(0, len(elevatedNodesLeft) - 1)]
                                randNode = elevatedNodesToUse[randIndex]
                                elevatedNodesLeft.remove(randIndex)
                                markedForChange = []
                                for regionElevatedNode in elevatedNodesToUse:
                                    if regionElevatedNode != randNode:
                                        dist = distToSplit(randNode, regionElevatedNode)
                                        if dist <= 18:
                                            markedForChange.append(regionElevatedNode)
                                        else:
                                            if randNode in regionDataSave.get(continent):
                                                for entry in regionDataSave.get(continent).get(randNode):
                                                    dist = distToSplit(entry, regionElevatedNode)
                                                    if dist <= 18:
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

                    print(f'--Finished Continent #{continentRun}')

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
                for river in range(0, numRivers):
                    riverStartNode = self.regionData.get(region).get("Elevated")
                    riverStartNode = random.choices(riverStartNode, k=1)[0]
                    regionSearch = True
                    currentNode = riverStartNode
                    riverNodes = [riverStartNode]
                    maxRiverLength = 16
                    while regionSearch:
                        currentNX = currentNode % self.columns
                        currentNY = currentNode // self.columns
                        currentNodeEle = self.nodeTerrainData.get(currentNode).get("Elevation")
                        adjacentNodes = []
                        elevationArr = []
                        for row in range(max(currentNY-1, 0), min(currentNY+1+1, self.rows)):
                            for column in range(max(currentNX-1, 0), min(currentNX+1+1, self.columns)):
                                nodeNum = row * self.columns + column
                                elevation = self.nodeTerrainData.get(nodeNum).get("Elevation")
                                if elevation < currentNodeEle * 1.10:
                                    adjacentNodes.append(nodeNum)
                                    elevation = 100/pow(pow(math.e, elevation), 2)
                                    elevationArr.append(elevation)

                        if len(adjacentNodes) < 1 or len(riverNodes) > maxRiverLength:
                            regionSearch = False
                        else:
                            currentNode = random.choices(adjacentNodes, elevationArr, k=1)[0]
                            riverNodes.append(currentNode)

                            if currentNode in waterNodes:
                                regionSearch = False
                    for nodeNum in riverNodes:
                        self.nodeTerrainData[nodeNum]["River"] = riverStartNode
                    riverDict = {
                        "Nodes": riverNodes,
                        "Start": riverStartNode,
                        "End": currentNode
                    }
                    self.riverDict[region] = riverDict

            print('-River Generation Complete')

            print('Begining River Spread')
            for river in self.riverDict:
                for nodeNum in self.riverDict.get(river).get("Nodes"):
                    designatedTerrain = self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")
                    self.nodeTerrainData[nodeNum]["ChosenTerrain"] = random.choices(self.terrainTypes.get(designatedTerrain).get("Wet"), k=1)[0]
                    self.terrainRecord[designatedTerrain].remove(nodeNum)
                    self.terrainRecord[self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")].append(nodeNum)
            print('-River Spread Complete')

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
                    temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 20
                    fetchedWeight = max(fetchedWeight - pow(temp, 1.1), 1)
                    allowedTerrainsWeight.append(fetchedWeight)
                elif terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                    allowedTerrainsForLAT.append(terrainEntry)
                    fetchedWeight = self.terrainTypes.get(terrainEntry).get("NodeSelChance")
                    # Fetch our distance from the center of the range
                    temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 20
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
            return pow(pow(nodeNum2x - nodeNum1x, 2) + pow(nodeNum2y - nodeNum1y, 2), 0.5)

        def assignRegions(terrainArr, regionSpawnTile):
            output = None
            proxyTArr = []
            designatedWeightsArr = []
            for terrainType in self.terrainTypes:
                # noinspection PyTypeChecker
                weight = pow(self.terrainTypes.get(terrainType).get("RegionSelChance") / (self.terrainRecord.get(terrainType) + 1), 0.4)
                designatedWeightsArr.append(weight)

            output = random.choices(terrainArr, designatedWeightsArr, k=1)[0]
            self.terrainRecord[output] += 1
            return output

        nodeTerrainData = dict()

        regionSpawnTiles = []
        maxNodes = self.rows * self.height
        for currentRegionSpawn in range(int(pow(self.rows * self.height, 0.4))):
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
                weightUsed = self.terrainTypes.get(regionTerrain).get("NodeSelChance") - pow(distance, 1.2 - self.terrainTypes.get(regionTerrain).get("Diffusion"))
                if distance > 10:
                    weightUsed = max(weightUsed, pow(2 * (pow(distance, 2.7) / pow(distance, 3)), 7))
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

    def getContinentData(self):
        return self.continentData

    def getRegionData(self):
        return self.regionData

    def fetchStageModifier(self):
        return self.stageModifier

    def advanceStageModifier(self):
        # NOTE-- this will result in regenerating the map
        self.stageModifier += 1

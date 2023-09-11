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
        self.rows, self.columns = 256, 144
        pygame.init()
        self.elevationGrid = dict()

        # Seed must have all 0-9 numbers, and be within 24 digits

        seed = 544786120398304714620491
        random.seed(544786120398304714620491)

        # self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor+self.adjustFactor*8))

        self.terrainTypes = {
            "Forest": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.25,
            },
            "Grassland": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.10,
            },
            "Plains": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": 0.05,
            },
            "Desert": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": -0.05,
            },
            "Hills": {
                "RegionSelChance": 20,
                "NodeSelChance": 30,
                "Diffusion": -0.10,
            },
            "Mountains": {
                "RegionSelChance": 30,
                "NodeSelChance": 30,
                "Diffusion": -0.15,
            }
        }

        self.terrainRecord = dict()
        for terrainType in self.terrainTypes:
            self.terrainRecord[terrainType] = 0

        startTime = time.time()
        print('Begining generation...')
        self.generateMap()
        print(f'We finished map generation-- this took {time.time()-startTime} seconds')

    # noinspection PyPep8Naming
    def generateMap(self):
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
            nodeTerrainData[regionSpawn]["Weight"] = [self.terrainTypes.get(designatedTerrain).get("NodeSelWeight")]

        for currentIteration in range(0, maxNodes - len(regionSpawnTiles)):
            selectedNode = random.randint(0, maxNodes - 1)
            success = False
            while not success:
                if selectedNode in nodeTerrainData:
                    if "ChosenTerrain" not in nodeTerrainData.get(selectedNode):
                        success = True
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

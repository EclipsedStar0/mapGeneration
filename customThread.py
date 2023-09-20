import threading


# noinspection PyPep8Naming
class noiseGenThread(threading.Thread):
    def __init__(self, noiseInstance, cX, cY, precision, factorAdjust, nxDictFed, nyFed):
        threading.Thread.__init__(self)
        self.noiseInstance = noiseInstance
        self.column = cX
        self.row = cY
        self.designatedPrecision = precision
        self.factorAdjust = factorAdjust
        self.noiseVal = 0

        self.nxDictGet = nxDictFed.get(self.column)
        self.nyGet = nyFed

    def run(self):
        for precision in range(self.designatedPrecision):
            self.noiseVal += 1 / pow(2, precision) * (self.noiseInstance.noise((pow(2, precision) * self.nxDictGet, pow(2, precision) * self.nyGet)))

        modifier = -1
        if self.noiseVal >= 0: modifier = 1
        self.noiseVal = modifier * pow(abs(self.noiseVal), self.factorAdjust)

    def getVal(self):
        return self.noiseVal, self.column, self.row


# noinspection PyPep8Naming
class mapRadialSearchThread(threading.Thread):
    def __init__(self, nodeX, nodeY, cX, cY, rows, columns, radialSearch, terrainTypes, nodeTerrainData):
        threading.Thread.__init__(self)
        self.diffuseWeight = 0
        self.nodeX, self.nodeY = nodeX, nodeY
        self.cX, self.cY = cX, cX
        self.rows, self.columns = rows, columns
        self.radialSearch = radialSearch
        self.terrainTypes = terrainTypes
        self.nodeTerrainData = nodeTerrainData
        self.mode = False
        self.diffuseTerrain = 'None'

    def run(self):
        distToDiffuseNode = pow(pow(self.nodeX-self.cX, 2)+pow(self.nodeY-self.cY, 2), 0.5)
        diffuseNodeNum = self.cY * self.columns + self.cX
        if distToDiffuseNode <= self.radialSearch:
            self.mode = True
            # We fall within the boundaries to affect this node
            diffuseTerrainInfo = self.nodeTerrainData.get(diffuseNodeNum)
            if diffuseTerrainInfo is not None:
                if diffuseTerrainInfo.get("ChosenTerrain") is not None:
                    self.diffuseTerrain = diffuseTerrainInfo.get("ChosenTerrain")
                    terrainPTQ = self.terrainTypes.get(self.diffuseTerrain).get("PTQ")
                    lattitudePQT = 100 - abs(1 - 2 * self.cY / self.rows) * 100

                    self.diffuseWeight = self.terrainTypes.get(self.diffuseTerrain).get("NodeSelChance")
                    if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                        # Fetch our distance from the center of the range
                        temp = abs(lattitudePQT - abs(terrainPTQ[0] - abs(terrainPTQ[1] - terrainPTQ[0]) / 2)) / 50
                        self.diffuseWeight = max(self.diffuseWeight - pow(temp, 1.1), 1)
                    else:
                        terrainHPTQ = self.terrainTypes.get(self.diffuseTerrain).get("HPTQ")
                        if terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                            # Fetch our distance from the center of the range
                            temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 50
                            self.diffuseWeight = max(self.diffuseWeight - pow(temp, 2.5), 1)
                        else:
                            temp = abs(lattitudePQT - abs(terrainHPTQ[0] - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2)) / 50
                            self.diffuseWeight = 0.25 * max(self.diffuseWeight - pow(temp, 3.25), 1)
                            # diffuseWeight *= 0.25
                    self.diffuseWeight = self.diffuseWeight / pow(distToDiffuseNode - 0.75, 0.7)
                else:
                    self.mode = False
            else:
                self.mode = False

    def getVal(self):
        return self.diffuseWeight, self.diffuseTerrain, self.mode

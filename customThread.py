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


# noinspection PyPep8Naming
class mapAssociatedElevThread(threading.Thread):
    def __init__(self, nodeNum, tData, eleData, columns, rows):
        threading.Thread.__init__(self)
        self.nodeNum = nodeNum
        self.minNode = self.nodeNum
        self.nodeTerrainData = tData
        self.elevationBasePoints = eleData
        self.columns, self.rows = columns, rows

    def run(self):
        def distTo(nodeNum1x, nodeNum1y, nodeNum2):
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        nodeNumx, nodeNumy = self.nodeNum % self.columns, int(self.nodeNum / self.columns)
        if self.nodeNum not in self.elevationBasePoints:
            minDist, minNode = float('inf'), float('inf')
            for basePoint in self.elevationBasePoints:
                dist = distTo(nodeNumx, nodeNumy, basePoint)
                if dist < minDist:
                    minDist = dist
                    self.minNode = basePoint
                    if minDist <= 1:
                        break

    def getVal(self):
        return self.nodeNum, self.minNode


# noinspection PyPep8Naming
class mapCoastalConverEle(threading.Thread):
    def __init__(self, nodeNum, terrainData, terrainTypes, terrainRecord):
        threading.Thread.__init__(self)
        self.nodeNum = nodeNum
        self.nodeTerrainData = terrainData
        self.terrainTypes = terrainTypes
        self.terrainRecord = terrainRecord
        self.newTerrain = None
        self.prevTerrain = None

    def run(self):
        designatedTerrain = self.nodeTerrainData.get(self.nodeNum).get("ChosenTerrain")
        self.prevTerrain, self.newTerrain = designatedTerrain, designatedTerrain
        nodeElevation = self.nodeTerrainData.get(self.nodeNum).get("Elevation")
        if nodeElevation < -1:
            self.newTerrain = "Ocean"
        elif nodeElevation < 1:
            self.newTerrain = "Coastal"
        elif nodeElevation < 1.5:
            self.newTerrain = self.terrainTypes.get(designatedTerrain).get("Wet")
        elif nodeElevation > 10:
            self.newTerrain = self.terrainTypes.get(designatedTerrain).get("Dry")

    def getVal(self):
        return self.newTerrain, self.prevTerrain, self.nodeNum

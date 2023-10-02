import threading


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
                    diffusionVal = self.terrainTypes.get(self.diffuseTerrain).get("Diffusion")
                    if terrainPTQ[0] <= lattitudePQT <= terrainPTQ[1]:
                        # Fetch our distance from the center of the range
                        temp = abs(lattitudePQT - abs(terrainPTQ[1] - terrainPTQ[0]) / 2) / 50
                        self.diffuseWeight = max(self.diffuseWeight - pow(temp, 1.1), 0)
                    else:
                        terrainHPTQ = self.terrainTypes.get(self.diffuseTerrain).get("HPTQ")
                        if terrainHPTQ[0] <= lattitudePQT <= terrainHPTQ[1]:
                            # Fetch our distance from the center of the range
                            temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                            self.diffuseWeight = max(self.diffuseWeight - pow(temp, 2.5), 0)
                        else:
                            temp = abs(lattitudePQT - abs(terrainHPTQ[1] - terrainHPTQ[0]) / 2) / 50
                            self.diffuseWeight = 0.25 * max(self.diffuseWeight - pow(temp, 3.25), 0)
                            # diffuseWeight *= 0.25

                    if self.diffuseWeight > 0:
                        self.diffuseWeight = self.diffuseWeight + pow(self.diffuseWeight, diffusionVal)
                        # diffuseWeight *= 0.25
                        self.diffuseWeight = self.diffuseWeight / pow(distToDiffuseNode + 1, 0.7)
                        if self.diffuseWeight >= 1:
                            self.diffuseWeight = pow(self.diffuseWeight, diffusionVal + 1)
                    else:
                        self.diffuseWeight = 0
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
        self.alternate = self.nodeNum

    def run(self):
        def distTo(nodeNum1x, nodeNum1y, nodeNum2):
            nodeNum2x, nodeNum2y = nodeNum2 % self.columns, int(nodeNum2 / self.columns)
            return pow(pow(nodeNum2x-nodeNum1x, 2) + pow(nodeNum2y-nodeNum1y, 2), 0.5)

        nodeNumX, nodeNumY = self.nodeNum % self.columns, self.nodeNum // self.columns
        pnodeNumX, pnodeNumY = nodeNumX, nodeNumY
        if pnodeNumX > self.columns - 8:
            pnodeNumX = (pnodeNumX + 8) % self.columns
        elif nodeNumX < 8:
            pnodeNumX = (pnodeNumX - 8) % self.columns

        if pnodeNumY > self.rows - 8:
            pnodeNumY = (pnodeNumY + 8) % self.rows
        elif nodeNumY < 8:
            pnodeNumY = (pnodeNumY - 8) % self.rows
        self.alternate = pnodeNumY * self.columns + pnodeNumX

        if self.nodeNum not in self.elevationBasePoints:
            minDist, minNode = float('inf'), float('inf')
            for basePoint in self.elevationBasePoints:
                dist = distTo(nodeNumX, nodeNumY, basePoint)
                if self.alternate != self.nodeNum:
                    dist = min(distTo(pnodeNumX, pnodeNumY, basePoint), dist)

                if dist < minDist:
                    minDist = dist
                    self.minNode = basePoint
                    if minDist <= 1:
                        break

    def getVal(self):
        return self.nodeNum, self.minNode, self.alternate


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
        if nodeElevation < -4 and designatedTerrain != "Ocean":
            self.newTerrain = "Ocean"
        elif nodeElevation < 1.5 and designatedTerrain != "Coastal":
            self.newTerrain = "Coastal"
        elif nodeElevation < 4 and designatedTerrain != "Ocean" and designatedTerrain != "Coastal" and designatedTerrain != "Oasis" and designatedTerrain != "Ice":
            self.newTerrain = self.terrainTypes.get(designatedTerrain).get("Wet")
        elif nodeElevation > 10:
            self.newTerrain = self.terrainTypes.get(designatedTerrain).get("Dry")

    def getVal(self):
        return self.newTerrain, self.prevTerrain, self.nodeNum

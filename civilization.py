# noinspection PyPep8Naming
class Civilization:
    def __init__(self, gameObj, civilizationID):
        self.territory = {
            "Hateful": dict(),
            "Subversive": dict(),
            "Disloyal": dict(),
            "Passive": dict(),
            "Cordial": dict(),
            "Loyal": dict(),
            "Capital": dict()
        }
        self.population = 0
        self.gameObj = gameObj
        self.economy = dict()
        self.civilizationID = civilizationID
        self.confirmed = True
        if self.civilizationID is None:
            self.confirmed = False

    def confirmedID(self, validID):
        self.civilizationID = validID
        self.confirmed = True

    def updatePopulation(self):
        for terrainLoyalty in self.territory:
            territoryInfo = self.territory.get(terrainLoyalty)
            for nodeNum in territoryInfo:
                nodeInfo = territoryInfo.get(nodeNum)
                self.territory[terrainLoyalty]["Population"] += nodeInfo.get("Population Growth")

    def updateTreasury(self):
        self.economy["IncomeLT"] = 0
        for terrainLoyalty in self.territory:
            territoryInfo = self.territory.get(terrainLoyalty)
            for nodeNum in territoryInfo:
                nodeObj = territoryInfo.get(nodeNum)
                taxVal = nodeObj.getSats().get("Tax")
                money = pow(taxVal*1.25, 1.3)
                self.economy["IncomeLT"] += money
        self.economy["Treasury"] += self.economy["IncomeLT"]

    def addTerritory(self, nodeObj):
        if nodeObj.getInfo().get("Controller") != self.civilizationID:
            nodeObj.nodeAnnexed(self)
            nodeLoyalty = nodeObj.getLoyalty().get(self.civilizationID)
            entry = "Subversive"
            if nodeLoyalty < 10: entry = "Hateful"
            elif nodeLoyalty < 30: entry = "Subversive"
            elif nodeLoyalty < 40: entry = "Disloyal"
            elif nodeLoyalty < 60: entry = "Passive"
            elif nodeLoyalty < 75: entry = "Cordial"
            elif nodeLoyalty < 100: entry = "Loyal"
            else: entry = "Capital"
            self.territory[entry][nodeObj.getNodeNum()] = nodeObj

    def removeTerritory(self, nodeObj):
        if nodeObj.getInfo().get("Controller") == self.civilizationID:
            nodeNum = nodeObj.getNodeNum()
            for territoryLoyalty in self.territory:
                if nodeNum in territoryLoyalty:
                    del self.territory[territoryLoyalty][nodeNum]
                    break

    def setCapital(self, nodeNum):
        nodeObj = self.gameObj.fetchWorldGenTerrainData().get(nodeNum)
        nodeObj.adjustLoyalty(self.civilizationID, 100)
        self.addTerritory(nodeObj)

    def getGameObj(self):
        return self.gameObj

    def getID(self):
        return self.civilizationID

    def getConfirmation(self):
        return self.confirmed

    def getTerritory(self):
        return self.territory

    def getCapital(self):
        capital = None
        # There should only be one capital
        for entry in self.territory.get("Capital"):
            capital = entry
            break
        return capital

    def getTotalPopulation(self):
        return self.population

    def getTreasury(self):
        return self.economy.get("Treasury")

    def getIncomeLT(self):
        return self.economy.get("IncomeLT")
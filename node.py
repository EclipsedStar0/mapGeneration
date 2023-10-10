from copy import deepcopy


# noinspection PyPep8Naming
class Node:
    def __init__(self, nodeNum, gameObj):
        self.nodeNum = nodeNum
        self.gameObj = gameObj
        # We are wiping this data by setting the nodeTerrainData dictionary to a new dict with the Node Objects, so we must copy the data
        self.nodeInfo = deepcopy(self.gameObj.fetchWorldGenTerrainData().get(nodeNum))
        self.nodeInfo["Controller"] = None
        self.nodeInfo["Loyalty"] = dict()
        self.nodeInfo["Stats"] = {
            "Health": 0,
            "Disease": 0,
            "Tax": 0,
            "Population": 0
        }
        self.nodeInfo["Resources"] = dict()

    def nodeAnnexed(self, newCiv):
        oldCivID = self.nodeInfo.get("Controller")
        fetchedCivs = self.gameObj.getCivilizationDict()
        if oldCivID in fetchedCivs:
            civObj = fetchedCivs.get(oldCivID)
            civObj.removeTerritory(self)

        self.nodeInfo["Controller"] = newCiv.getID()
        if newCiv.getID() not in self.nodeInfo.get("Loyalty"):
            self.nodeInfo["Loyalty"][newCiv.getID()] = 0

    def adjustLoyalty(self, civID, newLoyaltyVal):
        self.nodeInfo["Loyalty"][civID] = newLoyaltyVal

    def getGameObj(self):
        return self.gameObj

    def getNodeNum(self):
        return self.nodeNum

    def getInfo(self):
        return self.nodeInfo

    def getTerrainType(self):
        return self.nodeInfo.get("ChosenTerrain")

    def getWaterScore(self):
        return self.nodeInfo.get("WaterScore")

    def getElevation(self):
        return self.nodeInfo.get("Elevation")

    def getController(self):
        return self.nodeInfo.get("Controller")

    def getLoyalty(self):
        return self.nodeInfo.get('Loyalty')

    def getStats(self):
        return self.nodeInfo.get("Stats")

    def getResources(self):
        return self.getStats().get("Resources")
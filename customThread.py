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

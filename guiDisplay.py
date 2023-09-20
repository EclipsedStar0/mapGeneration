import pygame


# noinspection PyPep8Naming
class Display:
    def __init__(self, gameInstance):
        self.gameObj = gameInstance
        self.worldGen = self.gameObj.getWorldGen()
        self.adjustFactor = self.worldGen.getAdjustFactor()
        self.nodeTerrainData = self.worldGen.getTerrainData()
        self.terrainTypes = self.worldGen.getTerrainTypes()
        self.width, self.height = 1024, 576
        self.columns, self.rows = self.width // self.adjustFactor, self.height // self.adjustFactor

        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.width, self.height))
        self.generateDisplay()

    def generateDisplay(self):
        pass
        ''' Draw the display '''

        def drawTheInterface():
            self.SCREEN.fill((20, 10, 30))
            for row in range(0, self.rows):
                for column in range(0, self.columns):
                    nodeNum = row * self.columns + column
                    color = self.terrainTypes.get(self.nodeTerrainData.get(nodeNum).get("ChosenTerrain")).get("Color")
                    pygame.draw.rect(self.SCREEN, color, (self.adjustFactor * column, self.adjustFactor * row, self.adjustFactor, self.adjustFactor))

        drawTheInterface()
        pygame.display.update()

        '''User Interactions'''

        success = False
        while not success:
            for userEvent in pygame.event.get():
                pos = pygame.mouse.get_pos()
                playerRect = pygame.Rect(pos[0] - 1, pos[1] - 1, 2, 2)

                if userEvent.type == pygame.QUIT:
                    self.gameObj.endGame()

    def getDisplay(self):
        return self.SCREEN

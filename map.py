import sys

import perlin_noise
import pygame

# noinspection PyPep8Naming
class Map:
    def __init__(self):
        self.adjustFactor = 4
        self.width = int(1024/self.adjustFactor)
        self.height = int(576/self.adjustFactor)
        pygame.init()
        self.elevationGrid = dict()

        seed, designatedPrecision = 544786, 3
        self.noiseInstance = perlin_noise.PerlinNoise(seed)

        nxDict = dict()
        for column in range(self.width):
            nxDict[column] = column/self.width - 0.5

        total, miN, maX = self.width * self.height, float('inf'), 0
        adjustmentFactor = 3
        for row in range(self.height):
            self.elevationGrid[row] = dict()
            ny = row/self.height - 0.5
            for column in range(self.width):
                self.elevationGrid[row][column] = 0
                for precision in range(designatedPrecision):
                    self.elevationGrid[row][column] += 1/pow(2, precision) * (self.noiseInstance.noise((pow(2, precision) * nxDict.get(column), pow(2, precision) * ny)))
                self.elevationGrid[row][column] = pow(self.elevationGrid.get(row).get(column), adjustmentFactor)
                # print(self.elevationGrid.get(row).get(column))
                miN = min(miN, self.elevationGrid.get(row).get(column))
                maX = max(maX, self.elevationGrid.get(row).get(column))
                print(f'Progress: {100*(row*self.width + column) / total:0.6f}%')
        # print(miN, maX)
        self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor))
        self.displayMap(miN, maX)

    def displayMap(self, mini, maxi):

        self.SCREEN.fill((250, 50, 50))
        total = self.width * self.height
        mult = 1/(maxi - mini) * 255
        for row in range(self.height):
            rowFetch = self.elevationGrid.get(row)
            for column in range(self.width):
                elevation = mult * (rowFetch.get(column) + abs(mini))
                # print(elevation)
                red, green, blue = int(min(max(3*(elevation-190), 0), 255)), int(min(max(255*elevation, 0), 255)), int(min(max((255-elevation) * 2.5, 0), 255))
                print(rowFetch.get(column), (rowFetch.get(column)+abs(mini))*mult, red, green, blue)
                pygame.draw.rect(self.SCREEN, (red, green, blue), (column*self.adjustFactor, row*self.adjustFactor, self.adjustFactor, self.adjustFactor))
                # print(f'Progress: {100 * (row * self.width + column) / total:0.6f}%')
        print(maxi - mini, maxi, mini)
        pygame.display.update()

        success = False
        while not success:
            for userEvent in pygame.event.get():
                if userEvent.type == pygame.QUIT:
                    sys.exit()

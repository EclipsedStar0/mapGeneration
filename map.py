import math
import sys
import time

import perlin_noise
import pygame

import customThread


# noinspection PyPep8Naming
class Map:
    def __init__(self):
        self.adjustFactor = 8
        self.width = int(1024/self.adjustFactor)
        self.height = int(576/self.adjustFactor)
        pygame.init()
        self.elevationGrid = dict()

        seed, designatedPrecision = 544786, 3
        self.noiseInstance = perlin_noise.PerlinNoise(seed)

        nxDict = dict()
        for column in range(self.width):
            nxDict[column] = column/self.width - 0.5

        total, miN, maX = self.height, float('inf'), 0
        self.adjustmentFactor = 1

        prevRowStartTime = time.time()
        totalTime = 0
        for row in range(self.height):
            self.elevationGrid[row] = dict()
            ny = row/self.height - 0.5
            runningThreads = []
            totalTime += (time.time()-prevRowStartTime)
            print(f'Progress: {100 * row / total:0.6f}%: {totalTime/(row+1):0.6f}')
            prevRowStartTime = time.time()
            for column in range(self.width):
                # self.elevationGrid[row][column] = 0
                newThread = customThread.noiseGenThread(self.noiseInstance, column, row, designatedPrecision, self.adjustmentFactor, nxDict, ny)
                newThread.start()
                runningThreads.append(newThread)

                ''' 
                for precision in range(designatedPrecision):
                    self.elevationGrid[row][column] += 1/pow(2, precision) * (self.noiseInstance.noise((pow(2, precision) * nxDict.get(column), pow(2, precision) * ny)))

                modifier = -1
                if self.elevationGrid.get(row).get(column) >= 0: modifier = 1
                self.elevationGrid[row][column] = modifier * pow(abs(self.elevationGrid.get(row).get(column)), adjustmentFactor)
                '''
                # print(self.elevationGrid.get(row).get(column))
                # miN = min(miN, self.elevationGrid.get(row).get(column))
                # maX = max(maX, self.elevationGrid.get(row).get(column))

            for thread in runningThreads:
                thread.join()
                temp = thread.getVal()
                self.elevationGrid[temp[2]][temp[1]] = temp[0]
                miN = min(temp[0], miN)
                maX = max(temp[0], maX)
            '''
            while len(runningThreads) > 0:
                removedThreads = []
                for thread in runningThreads:
                    if not thread.is_alive():
                        removedThreads.append(thread)
                        thread.join()
                        temp = thread.getVal()
                        self.elevationGrid[temp[2]][temp[1]] = temp[0]
                        miN = min(temp[0], miN)
                        maX = max(temp[0], maX)
                for thread in removedThreads:
                    runningThreads.remove(thread)
            '''

        # print(miN, maX)
        self.SCREEN = pygame.display.set_mode((self.width*self.adjustFactor, self.height*self.adjustFactor+self.adjustFactor*8))
        self.displayMap(miN, maX)

    def displayMap(self, mini, maxi):

        self.SCREEN.fill((20, 10, 30))
        total = self.width * self.height
        mult = 255/(maxi - mini)

        # I want lower 20% to be water
        # I want 20-50 to be blue-green
        # I want 50-75 to be yellowish
        # I want 75 on to start getting redder

        buttonArr = dict()
        buttonSecondaryArr = dict()
        buttonSecondaryArr["RedMult"] = 12
        buttonSecondaryArr["RedPow"] = 2
        buttonSecondaryArr["SineVal"] = 6
        buttonSecondaryArr["SineDivisor"] = 63
        buttonSecondaryArr["BlueMult"] = 3
        buttonSecondaryArr["BluePow"] = 1.3
        buttonSecondaryArr["FactorAdjust"] = self.adjustmentFactor
        buttonSecondaryArr["BiomeView"] = 0
        buttonColorArr = dict()
        buttonColorArr["RedMult"] = (160, 0, 0)
        buttonColorArr["RedPow"] = (180, 0, 0)
        buttonColorArr["SineVal"] = (0, 160, 0)
        buttonColorArr["SineDivisor"] = (0, 180, 0)
        buttonColorArr["BlueMult"] = (0, 0, 160)
        buttonColorArr["BluePow"] = (0, 0, 180)
        buttonColorArr["FactorAdjust"] = (20, 20, 20)
        buttonColorArr["BiomeView"] = (20, 20, 20)
        '''
        buttonArr["SineVal"] = None
        buttonArr["blueMult"] = None
        buttonArr["bluePow"] = None
        buttonArr["SineDivisor"] = None
        buttonArr["RedMult"] = None
        buttonArr["RedPow"] = None
        '''

        def glow(color):
            return max(color[0] + 15, 0), min(color[1] + 25, 255), min(color[2] + 40, 255)

        def drawTheScreen():
            self.SCREEN.fill((20, 10, 30))
            for row in range(self.height):
                rowFetch = self.elevationGrid.get(row)
                for column in range(self.width):
                    elevation = mult * (rowFetch.get(column) - mini)
                    # print(elevation)
                    if abs(buttonSecondaryArr.get("BiomeView")) % 2 == 0:
                        # Use heightmap
                        greenVal, blueVal = int(min(max(255*math.sin(elevation/buttonSecondaryArr.get("SineDivisor") + buttonSecondaryArr.get("SineVal")), 0), 255)), int(min(max((255-pow(elevation, buttonSecondaryArr.get("BluePow")) * buttonSecondaryArr.get("BlueMult")), 0), 255))
                        redVal = 0
                        if elevation >= 136:
                            # Otherwise we'll get an imaginary number
                            if elevation == 200 and buttonSecondaryArr.get("RedPow") <= 0:
                                redVal = int(min(max(abs(pow(buttonSecondaryArr.get("RedMult") * (64 * 64 - pow(elevation - 200, 0)), 0.5)) - 110, 0), 255))
                            else:
                                redVal = int(min(max(abs(pow(buttonSecondaryArr.get("RedMult") * (64 * 64 - pow(elevation - 200, buttonSecondaryArr.get("RedPow"))), 0.5)) - 110, 0), 255))
                        redVal = max(redVal, 0)
                    else:
                        # use biome map
                        redVal, greenVal, blueVal = 0, 0, 0
                        if elevation < 0.3 * 255:
                            redVal, greenVal, blueVal = 0, elevation * 2, 255 - elevation
                        elif elevation < 0.35 * 255:
                            redVal, greenVal, blueVal = (230, 252, 191)
                        elif elevation < 0.4 * 255:
                            redVal, greenVal, blueVal = (71, 182, 37)
                        elif elevation < 0.5 * 255:
                            redVal, greenVal, blueVal = (15, 114, 22)
                        elif elevation < 0.6 * 255:
                            redVal, greenVal, blueVal = (71, 182, 37)
                        elif elevation < 0.75 * 255:
                            redVal, greenVal, blueVal = (208, 176, 45)
                        elif elevation < 0.8 * 255:
                            redVal, greenVal, blueVal = (178, 121, 12)
                        elif elevation < 0.95 * 255:
                            redVal, greenVal, blueVal = 20, 20, 20
                        elif elevation <= 1 * 255:
                            redVal, greenVal, blueVal = 230, 230, 230

                    # print((rowFetch.get(column) - mini) * mult)
                    # print(rowFetch.get(column), (rowFetch.get(column) - mini)*mult, red, green, blue)
                    # print(redVal, greenVal, blueVal)
                    pygame.draw.rect(self.SCREEN, (redVal, greenVal, blueVal), (column*self.adjustFactor, row*self.adjustFactor, self.adjustFactor, self.adjustFactor))
                    # print(f'Progress: {100 * (row * self.width + column) / total:0.6f}%')

            buttonArr["RedMult"] = pygame.draw.rect(self.SCREEN, (160, 0, 0), (2 * self.adjustFactor, self.height * self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))
            buttonArr["RedPow"] = pygame.draw.rect(self.SCREEN, (180, 0, 0), (8 * self.adjustFactor, self.height * self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))

            buttonArr["SineVal"] = pygame.draw.rect(self.SCREEN, (0, 160, 0), (16*self.adjustFactor, self.height*self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))
            buttonArr["SineDivisor"] = pygame.draw.rect(self.SCREEN, (0, 180, 0), (22*self.adjustFactor, self.height*self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))

            buttonArr["BlueMult"] = pygame.draw.rect(self.SCREEN, (0, 0, 160), (30*self.adjustFactor, self.height*self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))
            buttonArr["BluePow"] = pygame.draw.rect(self.SCREEN, (0, 0, 180), (36*self.adjustFactor, self.height*self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))

            buttonArr["FactorAdjust"] = pygame.draw.rect(self.SCREEN, (20, 20, 20), (44 * self.adjustFactor, self.height * self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))
            buttonArr["BiomeView"] = pygame.draw.rect(self.SCREEN, (20, 20, 20), (50 * self.adjustFactor, self.height * self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))

            x = pygame.draw.rect(self.SCREEN, (0, 0, 180), (36 * self.adjustFactor, self.height * self.adjustFactor + self.adjustFactor, self.adjustFactor * 4, self.adjustFactor * 2))

            for number in range(0, 256):
                if abs(buttonSecondaryArr.get("BiomeView")) % 2 == 0:
                    # Use heightmap
                    greenVal, blueVal = int(min(max(255 * math.sin(number / buttonSecondaryArr.get("SineDivisor") + buttonSecondaryArr.get("SineVal")), 0), 255)), int(
                        min(max((255 - pow(number, buttonSecondaryArr.get("BluePow")) * buttonSecondaryArr.get("BlueMult")), 0), 255))
                    redVal = 0
                    if number >= 136:
                        # Otherwise we'll get an imaginary number
                        if number == 200 and buttonSecondaryArr.get("RedPow") <= 0:
                            redVal = int(min(max(abs(pow(buttonSecondaryArr.get("RedMult") * (64 * 64 - pow(number - 200, 0)), 0.5)) - 110, 0), 255))
                        else:
                            redVal = int(min(max(abs(pow(buttonSecondaryArr.get("RedMult") * (64 * 64 - pow(number - 200, buttonSecondaryArr.get("RedPow"))), 0.5)) - 110, 0), 255))
                    redVal = max(redVal, 0)
                else:
                    # use biome map
                    redVal, greenVal, blueVal = 0, 0, 0
                    if number < 0.3 * 255:
                        redVal, greenVal, blueVal = 0, number * 2, 255 - number
                    elif number < 0.35 * 255:
                        redVal, greenVal, blueVal = (230, 252, 191)
                    elif number < 0.4 * 255:
                        redVal, greenVal, blueVal = (71, 182, 37)
                    elif number < 0.5 * 255:
                        redVal, greenVal, blueVal = (15, 114, 22)
                    elif number < 0.6 * 255:
                        redVal, greenVal, blueVal = (71, 182, 37)
                    elif number < 0.75 * 255:
                        redVal, greenVal, blueVal = (208, 176, 45)
                    elif number < 0.8 * 255:
                        redVal, greenVal, blueVal = (178, 121, 12)
                    elif number < 0.95 * 255:
                        redVal, greenVal, blueVal = 20, 20, 20
                    elif number <= 1 * 255:
                        redVal, greenVal, blueVal = 230, 230, 230

                pygame.draw.rect(self.SCREEN, (redVal, greenVal, blueVal), (number, self.height * self.adjustFactor + self.adjustFactor * 6, 1, self.adjustFactor * 2))

            # print(maxi - mini, maxi, mini)

        drawTheScreen()
        pygame.display.update()

        success = False
        clickTimes = 0

        changed = None
        while not success:
            for userEvent in pygame.event.get():
                pos = pygame.mouse.get_pos()
                playerRect = pygame.Rect(pos[0] - 1, pos[1] - 1, 2, 2)

                if userEvent.type == pygame.QUIT:
                    sys.exit()

                if userEvent.type == pygame.MOUSEMOTION:
                    buttonCollision = playerRect.collidedict(buttonArr, True)
                    if buttonCollision is not None:
                        changed = buttonCollision[0]

                        # noinspection PyTypeChecker
                        pygame.draw.rect(self.SCREEN, glow(buttonColorArr[buttonCollision[0]]), (buttonCollision[1].x, buttonCollision[1].y, buttonCollision[1].width, buttonCollision[1].height))

                        # buttonSecondaryArr[buttonCollision[0]] += 1

                        pygame.display.update()
                    else:
                        if changed is not None:
                            changeRect = buttonArr.get(changed)

                            # noinspection PyTypeChecker
                            pygame.draw.rect(self.SCREEN, buttonColorArr[changed], (changeRect.x, changeRect.y, changeRect.width, changeRect.height))

                            changed = None
                            pygame.display.update()

                if userEvent.type == pygame.MOUSEBUTTONDOWN and (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]):
                    buttonCollision = playerRect.collidedict(buttonArr, True)
                    if buttonCollision is not None:
                        intervalAmount = 1

                        if buttonCollision[0] == "SineDivisor":
                            intervalAmount = 2
                        elif buttonCollision[0] == "SinVal":
                            intervalAmount = 0.5
                        elif buttonCollision[0] == "BlueMult":
                            intervalAmount = 0.5
                        elif buttonCollision[0] == "BluePow":
                            intervalAmount = 0.1
                        elif buttonCollision[0] == "RedPow":
                            intervalAmount = 0.1
                        elif buttonCollision[0] == "RedMult":
                            intervalAmount = 2
                        elif buttonCollision[0] == "FactorAdjust":
                            intervalAmount = 0.2
                            if pygame.mouse.get_pressed()[2]: intervalAmount *= -1
                            self.adjustmentFactor += intervalAmount
                            mini, maxi = self.regenerate()

                        if pygame.mouse.get_pressed()[2]: intervalAmount *= -1

                        # noinspection PyTypeChecker
                        buttonSecondaryArr[buttonCollision[0]] += intervalAmount
                        drawTheScreen()
                        # noinspection PyTypeChecker
                        pygame.draw.rect(self.SCREEN, glow(buttonColorArr[buttonCollision[0]]), (buttonCollision[1].x, buttonCollision[1].y, buttonCollision[1].width, buttonCollision[1].height))
                        pygame.display.update()

                        print(f'clicked: {buttonCollision[0]}, {self.adjustmentFactor}')

    def regenerate(self):
        seed, designatedPrecision = 544786, 3
        # self.noiseInstance = perlin_noise.PerlinNoise(seed)

        nxDict = dict()
        for column in range(self.width):
            nxDict[column] = column / self.width - 0.5

        total, miN, maX = self.height, float('inf'), 0
        adjustmentFactor = self.adjustmentFactor

        prevRowStartTime = time.time()
        totalTime = 0
        for row in range(self.height):
            self.elevationGrid[row] = dict()
            ny = row / self.height - 0.5
            runningThreads = []
            totalTime += (time.time() - prevRowStartTime)
            print(f'Progress: {100 * row / total:0.6f}%: {totalTime / (row + 1):0.6f}')
            prevRowStartTime = time.time()
            for column in range(self.width):
                # self.elevationGrid[row][column] = 0
                newThread = customThread.noiseGenThread(self.noiseInstance, column, row, designatedPrecision, adjustmentFactor, nxDict, ny)
                newThread.start()
                runningThreads.append(newThread)

                ''' 
                for precision in range(designatedPrecision):
                    self.elevationGrid[row][column] += 1/pow(2, precision) * (self.noiseInstance.noise((pow(2, precision) * nxDict.get(column), pow(2, precision) * ny)))

                modifier = -1
                if self.elevationGrid.get(row).get(column) >= 0: modifier = 1
                self.elevationGrid[row][column] = modifier * pow(abs(self.elevationGrid.get(row).get(column)), adjustmentFactor)
                '''
                # print(self.elevationGrid.get(row).get(column))
                # miN = min(miN, self.elevationGrid.get(row).get(column))
                # maX = max(maX, self.elevationGrid.get(row).get(column))

            for thread in runningThreads:
                thread.join()
                temp = thread.getVal()
                self.elevationGrid[temp[2]][temp[1]] = temp[0]
                miN = min(temp[0], miN)
                maX = max(temp[0], maX)
            '''
            while len(runningThreads) > 0:
                removedThreads = []
                for thread in runningThreads:
                    if not thread.is_alive():
                        removedThreads.append(thread)
                        thread.join()
                        temp = thread.getVal()
                        self.elevationGrid[temp[2]][temp[1]] = temp[0]
                        miN = min(temp[0], miN)
                        maX = max(temp[0], maX)
                for thread in removedThreads:
                    runningThreads.remove(thread)
            '''
        return miN, maX
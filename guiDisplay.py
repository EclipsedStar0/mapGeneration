import time

import pygame


# noinspection PyPep8Naming
class Display:
    def __init__(self, gameInstance):
        self.gameObj = gameInstance
        self.worldGen = self.gameObj.getWorldGen()
        self.adjustFactor = self.worldGen.getAdjustFactor()
        self.continentData = self.worldGen.getContinentData()
        self.regionData = self.worldGen.getRegionData()
        self.nodeTerrainData = self.worldGen.getTerrainData()
        self.terrainTypes = self.worldGen.getTerrainTypes()
        self.width, self.height = 1024, 576
        self.addedHeight = 50
        self.columns, self.rows = self.width // self.adjustFactor, self.height // self.adjustFactor
        self.zoomLevel = 1
        self.centerPosX, self.centerPosY = int(self.width / self.adjustFactor / 2), int(self.height / self.adjustFactor / 2)
        self.Clock = pygame.time.Clock()
        # Adding some extra height just for buttons
        # Adding some extra height just for buttons
        self.height += self.addedHeight

        self.guiDisplayData = dict()

        self.totalGUITime = 0
        self.totalGUIRuns = 0

        pygame.init()
        self.SCREEN = pygame.display.set_mode((self.width, self.height))
        # self.generateDisplay()

    def generateDisplay(self):
        # Clear the stored data as we're regenerating the display from scratch
        self.guiDisplayData = dict()
        ''' Draw the display '''

        def glow(rgbTuple):
            redC, greenC, blueC = rgbTuple
            if redC > greenC:
                if redC > blueC:
                    redC = int(max(min(redC + 85, 255), 0))
                else:
                    blueC = int(max(min(blueC + 85, 255), 0))
            elif greenC > blueC:
                greenC = int(max(min(greenC + 85, 255), 0))
            else:
                blueC = int(max(min(blueC + 85, 255), 0))
            redC = int(max(min(redC - 35, 255), 0))
            greenC = int(max(min(greenC - 35, 255), 0))
            blueC = int(max(min(blueC - 35, 255), 0))
            return redC, greenC, blueC

        def greyOut(rgbTuple):
            redC, greenC, blueC = rgbTuple
            redC = int(max(min(redC - 35, 255), 20))
            greenC = int(max(min(greenC - 50, 255), 20))
            blueC = int(max(min(blueC - 75, 255), 20))
            return redC, greenC, blueC

        def drawTheInterface(politicalOn=True):
            guiStart = time.time()
            screenSurface = pygame.Surface((self.width, self.height))
            politicalSurface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
            screenSurface.fill((20, 10, 30))
            mode = self.guiDisplayData.get("Mode")
            if mode is None:
                self.guiDisplayData["Mode"] = "Terrain"
                mode = "Terrain"

            # Draw Terrain Data
            rowArr = []
            adjustedRowArr = []
            columnArr = []
            adjustedColumnArr = []
            '''searchRadiusY = int((self.rows * self.adjustFactor) // pow(2, self.zoomLevel - 1))
            searchRadiusX = int((self.columns * self.adjustFactor) // pow(2, self.zoomLevel - 1))
            for guiY in range(self.centerPosY - searchRadiusY, self.centerPosY + searchRadiusY):
                row = guiY % self.rows
                pRow = guiY
                for guiX in range(self.centerPosX - searchRadiusX, self.centerPosX + searchRadiusX):
                    column = guiX % self.columns
                    pColumn = guiX'''

            xFactor = int(self.width / 2 - self.centerPosX)
            yFactor = int((self.height - self.addedHeight) / 2 - self.centerPosY)
            for row in range(0, self.rows):
                for column in range(0, self.columns):

            # for pRow in range(int(self.centerPosY - self.rows // self.zoomLevel), int(self.centerPosY + self.rows // self.zoomLevel)):
                # row = pRow % self.rows
                # rowArr.append(pRow)
                # adjustedRowArr.append(row)
                # for pColumn in range(int(self.centerPosX - self.columns // (2 * self.zoomLevel)), int(self.centerPosX + self.columns // (2 * self.zoomLevel))):
                    # column = pColumn % self.columns
                    # if len(rowArr) == 1:
                        # columnArr.append(pColumn)
                        # adjustedColumnArr.append(column)
                    nodeNum = row * self.columns + column
                    color = (0, 0, 0)
                    if mode == "Terrain":
                        color = self.terrainTypes.get(self.nodeTerrainData.get(nodeNum).getTerrainType()).get("Color")
                    elif mode == "Simple":
                        color = (0, 0, 0)
                        typeOTerrain = self.terrainTypes.get(self.nodeTerrainData.get(nodeNum).getTerrainType()).get("Type")
                        if typeOTerrain == "Water":
                            color = (0, 0, 120)
                        elif typeOTerrain == "Woodland":
                            color = (20, 130, 0)
                        elif typeOTerrain == "Flat":
                            color = (60, 170, 30)
                        elif typeOTerrain == "Elevated":
                            color = (40, 30, 10)
                    elif mode == "Elevation" or mode == "River":
                        nodeElevation = self.nodeTerrainData.get(nodeNum).getElevation()
                        designatedTerrain = self.nodeTerrainData.get(nodeNum).getTerrainType()
                        if nodeElevation is None:
                            print(f'ERROR! Node #{self.nodeTerrainData.get(nodeNum)} is missing elevation!')
                        if nodeElevation < -4 or designatedTerrain == "Ocean":
                            color = (0, 0, 60)
                        elif nodeElevation <= 1.5 or designatedTerrain == "Coastal":
                            color = (0, 0, 120)
                        elif nodeElevation < 4:
                            color = (255, 235, 205)
                        elif nodeElevation < 5:
                            color = (0, 180, 0)
                        elif nodeElevation < 6:
                            color = (0, 130, 0)
                        elif nodeElevation < 7:
                            color = (30, 130, 0)
                        elif nodeElevation < 8:
                            color = (50, 110, 0)
                        elif nodeElevation < 10:
                            color = (75, 60, 0)
                        elif nodeElevation < 12:
                            color = (120, 30, 0)
                        elif nodeElevation < 13:
                            color = (140, 25, 0)
                        elif nodeElevation < 14:
                            color = (160, 22, 0)
                        elif nodeElevation < 15:
                            color = (180, 20, 0)
                        else:
                            color = (230, 10, 0)
                    elif mode == "Continent":
                        continent = self.nodeTerrainData.get(nodeNum).getInfo().get("Continent")
                        color = (0, 0, 80)
                        if continent is None:
                            color = (0, 0, 0)
                        else:
                            designatedTerrain = self.nodeTerrainData.get(nodeNum).getTerrainType()
                            if designatedTerrain != "Ocean" and designatedTerrain != "Coastal":
                                color = self.continentData.get(continent).get("Color")
                                if nodeNum in self.continentData.get(continent).get("Elevated"):
                                    color = glow(color)
                    elif mode == "Region":
                        region = self.nodeTerrainData.get(nodeNum).getInfo().get("Region")
                        color = (0, 0, 80)
                        if region is None:
                            color = (0, 0, 0)
                        else:
                            designatedTerrain = self.nodeTerrainData.get(nodeNum).getTerrainType()
                            if designatedTerrain != "Ocean" and designatedTerrain != "Coastal":
                                color = self.regionData.get(region).get("Color")
                                if nodeNum in self.regionData.get(region).get("Elevated"):
                                    color = glow(color)
                    pygame.draw.rect(screenSurface, color, (self.adjustFactor * ((column + xFactor) % self.columns) * self.zoomLevel, self.adjustFactor * ((row + yFactor) % self.rows) * self.zoomLevel, self.adjustFactor * self.zoomLevel, self.adjustFactor * self.zoomLevel))

                    # print("---------------")
                    # print(pRow, pColumn)
                    # print(self.adjustFactor * pColumn * self.zoomLevel, self.adjustFactor * pRow * self.zoomLevel, self.adjustFactor * self.zoomLevel)

                    if mode == "River":
                        if "River" in self.nodeTerrainData.get(nodeNum).getInfo():
                            pygame.draw.circle(screenSurface, (0, 70, 220), (self.adjustFactor * ((column + xFactor) % self.columns) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel, self.adjustFactor * ((row + yFactor) % self.rows) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel), self.adjustFactor*2/3 * self.zoomLevel)

                    if politicalOn:
                        cInfo = self.nodeTerrainData.get(nodeNum).getInfo().get("Controller")
                        if cInfo is not None:
                            if cInfo in self.gameObj.getCivilizationDict():
                                cObj = self.gameObj.getCivilizationDict().get(cInfo)
                                if cObj.getCapital() == row * self.columns + column:
                                    pygame.draw.circle(politicalSurface, (230, 230, 230, 200), (self.adjustFactor * ((column + xFactor) % self.columns) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel, self.adjustFactor * ((row + yFactor) % self.rows) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel), self.adjustFactor*7/4 * self.zoomLevel)
                                pygame.draw.circle(politicalSurface, (230, 0, 0, 150), (self.adjustFactor * ((column + xFactor) % self.columns) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel, self.adjustFactor * ((row + yFactor) % self.rows) * self.zoomLevel + self.adjustFactor/2 * self.zoomLevel), self.adjustFactor*3/4 * self.zoomLevel)

            '''for row in range(self.rows):
                if row not in adjustedRowArr:
                    print(f'Missing row {row}')
            for column in range(self.columns):
                if column not in adjustedColumnArr:
                    print(f'Missing column {column}')
            print("-------------------------------------------------------------------------------------------------------")
            print(rowArr)
            print(adjustedRowArr)
            print()
            print(columnArr)
            print(adjustedColumnArr)
            print(min(adjustedRowArr), max(adjustedRowArr))
            print(min(adjustedColumnArr), max(adjustedColumnArr))'''

            # Draw bottom row buttons
            startHeight = self.height - self.addedHeight
            terrainC = (70, 170, 70)
            simpleC = (120, 230, 120)
            elevationC = (170, 70, 70)
            riverC = (20, 70, 220)
            continentC = (70, 70, 170)
            regionC = (120, 120, 190)
            politicalC = (220, 30, 150)
            advanceC = (190, 40, 190)
            turnAC = (120, 120, 120)

            fetchMod = self.worldGen.fetchStageModifier()

            if mode == "Terrain": terrainC = greyOut(terrainC)
            if mode == "Simple": simpleC = greyOut(simpleC)
            elif mode == "Elevation" or fetchMod < 1: elevationC = greyOut(elevationC)
            elif mode == "River" or fetchMod < 7: riverC = greyOut(riverC)
            elif mode == "Continent" or fetchMod < 5: continentC = greyOut(continentC)
            elif mode == "Region" or fetchMod < 6: regionC = greyOut(regionC)
            elif mode == "Turn Advance" or fetchMod < 4: turnAC = greyOut(turnAC)

            if politicalOn == "Political": politicalC = greyOut(politicalC)

            if fetchMod > 5:
                advanceC = greyOut(advanceC)

            terrainBTN = pygame.draw.rect(screenSurface, terrainC, (self.width * 0.05, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            simpleBTN = pygame.draw.rect(screenSurface, simpleC, (self.width * 0.12, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            elevationBTN = pygame.draw.rect(screenSurface, elevationC, (self.width * 0.19, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            riverBTN = pygame.draw.rect(screenSurface, riverC, (self.width * 0.26, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))

            continentBTN = pygame.draw.rect(screenSurface, continentC, (self.width * 0.40, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            regionBTN = pygame.draw.rect(screenSurface, regionC, (self.width * 0.47, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            politicalBTN = pygame.draw.rect(screenSurface, politicalC, (self.width * 0.54, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))

            advanceBTN = pygame.draw.rect(screenSurface, advanceC, (self.width * 0.74, startHeight + self.addedHeight / 3, self.width * 0.05, self.addedHeight / 3))
            turnAdvBTN = pygame.draw.circle(screenSurface, turnAC, (self.width * 0.81 + self.addedHeight / 6, startHeight + self.addedHeight / 3 + self.addedHeight / 6), self.addedHeight / 6)
            self.guiDisplayData["Buttons"] = {
                "Terrain": terrainBTN,
                "Simple": simpleBTN,
                "Elevation": elevationBTN,
                "River": riverBTN,
                "Continent": continentBTN,
                "Region": regionBTN,
                "Political": politicalBTN,
                "Advance Mode": advanceBTN,
                "Advance Turn": turnAdvBTN
            }

            self.totalGUITime += time.time() - guiStart
            self.totalGUIRuns += 1
            return screenSurface, politicalSurface

        politicalMapModeEngaged = True
        returnedScreenSurface, polSurface = drawTheInterface(politicalMapModeEngaged)
        self.SCREEN.blit(returnedScreenSurface, (0, 0))
        self.SCREEN.blit(polSurface, (0, 0))
        pygame.mouse.set_visible(False)
        cursorSurface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        cursorSurface.fill((0, 0, 0, 0))
        pos = pygame.mouse.get_pos()
        cursorCircle = pygame.draw.circle(cursorSurface, (20, 80, 140), (pos[0], pos[1]), 8)
        self.SCREEN.blit(cursorSurface, (0, 0))

        pygame.display.update()

        '''User Interactions'''

        success = False
        while not success:
            for userEvent in pygame.event.get():
                print(f'{self.totalGUITime / self.totalGUIRuns:.6f}')
                pos = pygame.mouse.get_pos()
                playerRect = pygame.Rect(pos[0] - 1, pos[1] - 1, 2, 2)
                seperator = True
                if seperator:
                    keysHeldDown = pygame.key.get_pressed()
                    updateMap = False
                    if keysHeldDown[pygame.K_w]:
                        self.centerPosY -= 2
                        updateMap = True
                    elif keysHeldDown[pygame.K_s]:
                        self.centerPosY += 2
                        updateMap = True
                    if keysHeldDown[pygame.K_a]:
                        self.centerPosX -= 2
                        updateMap = True
                    elif keysHeldDown[pygame.K_d]:
                        self.centerPosX += 2
                        updateMap = True

                    if updateMap:
                        self.centerPosX %= self.columns
                        self.centerPosY %= self.rows
                        returnedScreenSurface, polSurface = drawTheInterface()
                        self.SCREEN.blit(returnedScreenSurface, (0, 0))
                        self.SCREEN.blit(polSurface, (0, 0))
                        cursorSurface.fill((0, 0, 0, 0))
                        pos = pygame.mouse.get_pos()
                        cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                        self.SCREEN.blit(cursorSurface, (0, 0))
                        pygame.display.update()

                if userEvent.type == pygame.QUIT:
                    success = True
                    self.gameObj.endGame()

                elif userEvent.type == pygame.MOUSEWHEEL:
                    if userEvent.y < 0:
                        self.zoomLevel -= 1
                    else: self.zoomLevel += 1
                    self.zoomLevel = min(max(self.zoomLevel, 1), 16)
                    self.centerPosX += ((pos[0] / (self.adjustFactor * self.zoomLevel)) - self.centerPosX)
                    self.centerPosY += ((pos[1] / (self.adjustFactor * self.zoomLevel)) - self.centerPosY)
                    self.centerPosX %= self.columns
                    self.centerPosY %= self.rows
                    returnedScreenSurface, polSurface = drawTheInterface()
                    self.SCREEN.blit(returnedScreenSurface, (0, 0))
                    self.SCREEN.blit(polSurface, (0, 0))
                    cursorSurface.fill((0, 0, 0, 0))
                    pos = pygame.mouse.get_pos()
                    cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                    self.SCREEN.blit(cursorSurface, (0, 0))
                    pygame.display.update()

                elif userEvent.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        # We are left-clicking
                        # noinspection PyTypeChecker
                        mapModeBTNs = cursorCircle.collidedict(self.guiDisplayData.get("Buttons"), True)
                        if mapModeBTNs:
                            # noinspection PyUnresolvedReferences
                            buttonName = mapModeBTNs[0]
                            buttonCollidedWith = mapModeBTNs[1]
                            if self.guiDisplayData.get("Mode") != buttonName:
                                modifier = self.worldGen.fetchStageModifier()
                                valid = False
                                if buttonName == "Terrain" or buttonName == "Simple": valid = True
                                elif buttonName == "Elevation" and modifier > 1: valid = True
                                elif buttonName == "River" and modifier > 6: valid = True
                                elif buttonName == "Continent" and modifier > 4: valid = True
                                elif buttonName == "Region" and modifier > 5: valid = True
                                elif buttonName == "Advance Mode" and modifier < 7: valid = True
                                elif buttonName == "Advance Turn" and modifier >= 4: valid = True
                                elif buttonName == "Political" and modifier > 6: valid = True
                                if valid:
                                    if buttonName != "Advance Mode" and buttonName != "Advance Turn":
                                        if buttonName != "Political":
                                            self.guiDisplayData["Mode"] = buttonName
                                        else:
                                            politicalMapModeEngaged = not politicalMapModeEngaged
                                        returnedScreenSurface, polSurface = drawTheInterface(politicalMapModeEngaged)
                                        self.SCREEN.blit(returnedScreenSurface, (0, 0))
                                        self.SCREEN.blit(polSurface, (0, 0))
                                        cursorSurface.fill((0, 0, 0, 0))
                                        cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                                        self.SCREEN.blit(cursorSurface, (0, 0))
                                        pygame.display.update()
                                    else:
                                        if buttonName == "Advance Mode" and modifier < 7:
                                            self.worldGen.advanceStageModifier()
                                            startTime = time.time()
                                            print('\nBegining generation...')
                                            self.worldGen.generateMap()
                                            print(f'We finished map generation-- this took {time.time() - startTime} seconds')
                                            self.continentData = self.worldGen.getContinentData()
                                            self.regionData = self.worldGen.getRegionData()
                                            self.nodeTerrainData = self.worldGen.getTerrainData()
                                            self.terrainTypes = self.worldGen.getTerrainTypes()
                                            returnedScreenSurface, polSurface = drawTheInterface()
                                            self.SCREEN.blit(returnedScreenSurface, (0, 0))
                                            self.SCREEN.blit(polSurface, (0, 0))
                                            cursorSurface.fill((0, 0, 0, 0))
                                            pos = pygame.mouse.get_pos()
                                            cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                                            self.SCREEN.blit(cursorSurface, (0, 0))
                                            pygame.display.update()
                                        elif buttonName == "Advance Turn" and modifier > 3:
                                            pygame.draw.circle(cursorSurface, (0, 0, 0, 32), buttonCollidedWith.center, buttonCollidedWith.centerx-buttonCollidedWith.x)
                                            cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                                            self.SCREEN.blit(cursorSurface, (0, 0))
                                            pygame.display.update()

                                            success = True

                elif userEvent.type == pygame.MOUSEMOTION:
                    self.SCREEN.blit(returnedScreenSurface, (0, 0))
                    self.SCREEN.blit(polSurface, (0, 0))
                    cursorSurface.fill((0, 0, 0, 0))
                    # noinspection PyTypeChecker
                    mapModeBTNs = cursorCircle.collidedict(self.guiDisplayData.get("Buttons"), True)
                    if mapModeBTNs:
                        buttonName = mapModeBTNs[0]
                        buttonCollidedWith = mapModeBTNs[1]

                        if self.guiDisplayData.get("Mode") != buttonName:
                            modifier = self.worldGen.fetchStageModifier()
                            valid = False
                            if buttonName == "Terrain" or buttonName == "Simple": valid = True
                            elif buttonName == "Elevation" and modifier > 1: valid = True
                            elif buttonName == "River" and modifier > 6: valid = True
                            elif buttonName == "Continent" and modifier > 4: valid = True
                            elif buttonName == "Region" and modifier > 5: valid = True
                            elif buttonName == "Political" and modifier > 6: valid = True
                            elif buttonName == "Advance Mode" and modifier < 7: valid = True
                            elif buttonName == "Advance Turn" and modifier > 3: valid = True
                            if valid and buttonName != "Advance Turn":
                                pygame.draw.rect(cursorSurface, (255, 255, 255, 32), buttonCollidedWith)
                            elif valid:
                                pygame.draw.circle(cursorSurface, (255, 255, 255, 32), buttonCollidedWith.center, buttonCollidedWith.centerx-buttonCollidedWith.x)

                    cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                    self.SCREEN.blit(cursorSurface, (0, 0))
                    pygame.display.update()

                '''proxyCX, proxyCY = self.centerPosX, self.centerPosY
                numLevels = 6
                if pos[0] < self.width // 64:
                    threshold = self.width // 64
                    for level in range(0, numLevels):
                        if pos[0] < threshold:
                            threshold /= 2
                            self.centerPosX -= pow(2, level)
                        else: break

                elif pos[0] > 63 * self.width // 64:
                    threshold = 63 * self.width // 64
                    for level in range(0, numLevels):
                        if threshold < pos[0]:
                            threshold = (self.width + threshold) / 2
                            self.centerPosX += pow(2, level)
                        else: break

                if pos[1] < (self.height - self.addedHeight) // 64:
                    threshold = (self.height - self.addedHeight) // 64
                    for level in range(0, numLevels):
                        if pos[1] < threshold:
                            self.centerPosY += pow(2, level)
                            threshold /= 2
                        else: break

                elif pos[1] > 63 * (self.height - self.addedHeight) // 64:
                    threshold = 63 * (self.height - self.addedHeight) // 64
                    for level in range(0, numLevels):
                        if threshold < pos[1]:
                            threshold = (self.height - self.addedHeight + threshold) / 2
                            self.centerPosY -= pow(2, level)
                        else: break

                self.centerPosY %= self.rows
                self.centerPosX %= self.columns
                if proxyCX != self.centerPosX or proxyCY != self.centerPosY:
                    print(self.centerPosX, self.centerPosY)
                    returnedScreenSurface, polSurface = drawTheInterface()
                    self.SCREEN.blit(returnedScreenSurface, (0, 0))
                    self.SCREEN.blit(polSurface, (0, 0))
                    cursorSurface.fill((0, 0, 0, 0))
                    pos = pygame.mouse.get_pos()
                    cursorCircle = pygame.draw.circle(cursorSurface, (40, 240, 200, 255), (pos[0], pos[1]), 6)
                    self.SCREEN.blit(cursorSurface, (0, 0))
                    pygame.display.update()'''

            self.Clock.tick(25)

    def getDisplay(self):
        return self.SCREEN

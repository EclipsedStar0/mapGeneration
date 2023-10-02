class CodexValidationException(Exception):
    pass


# noinspection PyPep8Naming
class TerrainCodex:
    def __init__(self):
        self.codex = dict()

        seperateElement = True
        if seperateElement:
            terrainName = "Ocean"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 5
            self.codex[terrainName]["NodeSelChance"] = 2.75
            self.codex[terrainName]["Diffusion"] = 1.55
            self.codex[terrainName]["Color"] = (0, 0, 60)
            self.codex[terrainName]["PTQ"] = (20, 35)
            self.codex[terrainName]["HPTQ"] = (15, 40)
            self.codex[terrainName]["Wet"] = ["Ocean"]
            self.codex[terrainName]["Dry"] = ["Coastal", "Coastal", "Ocean"]
            self.codex[terrainName]["Similar"] = ["Coastal"]
            self.codex[terrainName]["EffectBonus"] = -2
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 2
            self.codex[terrainName]["Type"] = "Water"
        if seperateElement:
            terrainName = "Coastal"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 3.5
            self.codex[terrainName]["Diffusion"] = 2.35
            self.codex[terrainName]["Color"] = (0, 0, 120)
            self.codex[terrainName]["PTQ"] = (90, 110)
            self.codex[terrainName]["HPTQ"] = (80, 120)
            self.codex[terrainName]["Wet"] = ["Coastal", "Ocean", "Ocean", "Ocean"]
            self.codex[terrainName]["Dry"] = ["Desert", "Oasis", "Oasis", "Plains", "Plains"]
            self.codex[terrainName]["Similar"] = ["Ocean"]
            self.codex[terrainName]["EffectBonus"] = -1
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 1.5
            self.codex[terrainName]["Type"] = "Water"
        if seperateElement:
            terrainName = "Ice"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 15
            self.codex[terrainName]["NodeSelChance"] = 25
            self.codex[terrainName]["Diffusion"] = 0.25
            self.codex[terrainName]["Color"] = (255, 255, 255)
            self.codex[terrainName]["PTQ"] = (-25, 25)
            self.codex[terrainName]["HPTQ"] = (-28, 28)
            self.codex[terrainName]["Wet"] = ["Ice", "Coastal", "Coastal"]
            self.codex[terrainName]["Dry"] = ["Tundra", "Coastal"]
            self.codex[terrainName]["Similar"] = ["Tundra", "Taiga"]
            self.codex[terrainName]["EffectBonus"] = -4
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.5
            self.codex[terrainName]["Type"] = "Water"
        if seperateElement:
            terrainName = "Tundra"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 35
            self.codex[terrainName]["Diffusion"] = 0.05
            self.codex[terrainName]["Color"] = (230, 230, 230)
            self.codex[terrainName]["PTQ"] = (23, 35)
            self.codex[terrainName]["HPTQ"] = (15, 55)
            self.codex[terrainName]["Wet"] = ["Taiga", "Taiga", "Ice"]
            self.codex[terrainName]["Dry"] = ["Tundra"]
            self.codex[terrainName]["Similar"] = ["Taiga"]
            self.codex[terrainName]["EffectBonus"] = 0
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.25
            self.codex[terrainName]["Type"] = "Flat"
        if seperateElement:
            terrainName = "Taiga"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 35
            self.codex[terrainName]["Diffusion"] = 0.25
            self.codex[terrainName]["Color"] = (160, 180, 160)
            self.codex[terrainName]["PTQ"] = (25, 35)
            self.codex[terrainName]["HPTQ"] = (17, 59)
            self.codex[terrainName]["Wet"] = ["Taiga", "Taiga", "Forest"]
            self.codex[terrainName]["Dry"] = ["Tundra", "Tundra", "Tundra", "Tundra", "Forest"]
            self.codex[terrainName]["Similar"] = ["Tundra"]
            self.codex[terrainName]["EffectBonus"] = 0
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.25
            self.codex[terrainName]["Type"] = "Woodland"
        if seperateElement:
            terrainName = "Forest"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 15
            self.codex[terrainName]["Diffusion"] = 0.65
            self.codex[terrainName]["Color"] = (0, 60, 0)
            self.codex[terrainName]["PTQ"] = (44, 63)
            self.codex[terrainName]["HPTQ"] = (34, 85)
            self.codex[terrainName]["Wet"] = ["Forest"]
            self.codex[terrainName]["Dry"] = ["Grassland", "Grassland", "Plains"]
            self.codex[terrainName]["Similar"] = ["Grassland"]
            self.codex[terrainName]["EffectBonus"] = 2
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.40
            self.codex[terrainName]["Type"] = "Woodland"
        if seperateElement:
            terrainName = "Grassland"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 30
            self.codex[terrainName]["Diffusion"] = 0.10
            self.codex[terrainName]["Color"] = (70, 200, 50)
            self.codex[terrainName]["PTQ"] = (43, 68)
            self.codex[terrainName]["HPTQ"] = (33, 86)
            self.codex[terrainName]["Wet"] = ["Grassland", "Forest", "Forest"]
            self.codex[terrainName]["Dry"] = ["Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Savannah"]
            self.codex[terrainName]["Similar"] = ["Forest", "Plains"]
            self.codex[terrainName]["EffectBonus"] = 1
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.35
            self.codex[terrainName]["Type"] = "Flat"
        if seperateElement:
            terrainName = "Plains"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 35
            self.codex[terrainName]["Diffusion"] = 0.05
            self.codex[terrainName]["Color"] = (150, 200, 50)
            self.codex[terrainName]["PTQ"] = (70, 85)
            self.codex[terrainName]["HPTQ"] = (60, 87)
            self.codex[terrainName]["Wet"] = ["Grassland"]
            self.codex[terrainName]["Dry"] = ["Desert", "Desert", "Desert", "Desert", "Savannah", "Oasis"]
            self.codex[terrainName]["Similar"] = ["Grassland", "Savannah"]
            self.codex[terrainName]["EffectBonus"] = 0
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 0.15
            self.codex[terrainName]["Type"] = "Flat"
        if seperateElement:
            terrainName = "Savannah"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 5
            self.codex[terrainName]["NodeSelChance"] = 15
            self.codex[terrainName]["Diffusion"] = -0.3
            self.codex[terrainName]["Color"] = (170, 130, 80)
            self.codex[terrainName]["PTQ"] = (75, 90)
            self.codex[terrainName]["HPTQ"] = (65, 95)
            self.codex[terrainName]["Wet"] = ["Plains", "Plains", "Savannah", "Savannah", "Savannah", "Oasis"]
            self.codex[terrainName]["Dry"] = ["Desert", "Desert", "Savannah"]
            self.codex[terrainName]["Similar"] = ["Oasis"]
            self.codex[terrainName]["EffectBonus"] = -1
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = -0.75
            self.codex[terrainName]["Type"] = "Woodland"
        if seperateElement:
            terrainName = "Desert"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 25
            self.codex[terrainName]["Diffusion"] = -0.05
            self.codex[terrainName]["Color"] = (220, 190, 50)
            self.codex[terrainName]["PTQ"] = (80, 120)
            self.codex[terrainName]["HPTQ"] = (75, 125)
            self.codex[terrainName]["Wet"] = ["Savannah", "Savannah", "Savannah", "Oasis", "Oasis", "Oasis", "Oasis", "Oasis"]
            self.codex[terrainName]["Dry"] = ["Desert"]
            self.codex[terrainName]["Similar"] = ["Savannah", "Oasis"]
            self.codex[terrainName]["EffectBonus"] = -1
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = -2.25
            self.codex[terrainName]["Type"] = "Flat"
        if seperateElement:
            terrainName = "Oasis"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 5
            self.codex[terrainName]["Diffusion"] = -0.25
            self.codex[terrainName]["Color"] = (30, 175, 140)
            self.codex[terrainName]["PTQ"] = (90, 110)
            self.codex[terrainName]["HPTQ"] = (80, 120)
            self.codex[terrainName]["Wet"] = ["Oasis", "Oasis", "Oasis", "Oasis", "Oasis", "Coastal"]
            self.codex[terrainName]["Dry"] = ["Desert", "Desert", "Desert", "Desert", "Savannah"]
            self.codex[terrainName]["Similar"] = ["Desert"]
            self.codex[terrainName]["EffectBonus"] = -1
            # self.codex[terrainName]["SelfBonus"] = 0
            # self.codex[terrainName]["RangeBonus"] = 0
            self.codex[terrainName]["WaterScore"] = 1
            self.codex[terrainName]["Type"] = "Flat"
        if seperateElement:
            terrainName = "Steppe"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 2
            self.codex[terrainName]["NodeSelChance"] = 2
            self.codex[terrainName]["Diffusion"] = -0.25
            self.codex[terrainName]["Color"] = (150, 150, 120)
            self.codex[terrainName]["PTQ"] = (65, 95)
            self.codex[terrainName]["HPTQ"] = (43, 110)
            self.codex[terrainName]["Wet"] = ["Steppe"]
            self.codex[terrainName]["Dry"] = ["Steppe"]
            self.codex[terrainName]["Similar"] = ["Plains", "Savannah"]
            self.codex[terrainName]["EffectBonus"] = 4
            self.codex[terrainName]["SelfBonus"] = 2
            self.codex[terrainName]["RangeBonus"] = 2
            self.codex[terrainName]["WaterScore"] = 1
            self.codex[terrainName]["Type"] = "Elevated"
        if seperateElement:
            terrainName = "Hills"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 20
            self.codex[terrainName]["NodeSelChance"] = 5
            self.codex[terrainName]["Diffusion"] = -0.25
            self.codex[terrainName]["Color"] = (170, 150, 50)
            self.codex[terrainName]["PTQ"] = (25, 95)
            self.codex[terrainName]["HPTQ"] = (23, 100)
            self.codex[terrainName]["Wet"] = ["Hills"]
            self.codex[terrainName]["Dry"] = ["Hills"]
            self.codex[terrainName]["Similar"] = ["Steppe"]
            self.codex[terrainName]["EffectBonus"] = 5
            self.codex[terrainName]["SelfBonus"] = 4
            self.codex[terrainName]["RangeBonus"] = 3
            self.codex[terrainName]["WaterScore"] = -1.5
            self.codex[terrainName]["Type"] = "Elevated"
        if seperateElement:
            terrainName = "Mountains"
            self.codex[terrainName] = dict()
            self.codex[terrainName]["RegionSelChance"] = 30
            self.codex[terrainName]["NodeSelChance"] = 1
            self.codex[terrainName]["Diffusion"] = -0.35
            self.codex[terrainName]["Color"] = (50, 50, 70)
            self.codex[terrainName]["PTQ"] = (35, 85)
            self.codex[terrainName]["HPTQ"] = (10, 95)
            self.codex[terrainName]["Wet"] = ["Mountains"]
            self.codex[terrainName]["Dry"] = ["Mountains"]
            self.codex[terrainName]["Similar"] = ["Hills"]
            self.codex[terrainName]["EffectBonus"] = 8
            self.codex[terrainName]["SelfBonus"] = 5
            self.codex[terrainName]["RangeBonus"] = 5
            self.codex[terrainName]["WaterScore"] = -3
            self.codex[terrainName]["Type"] = "Elevated"

        self.validateCodex()

    def validateCodex(self):
        requiredAttrs = {
            "RegionSelChance": float,
            "NodeSelChance": float,
            "Diffusion": float,
            "Color": tuple,
            "PTQ": tuple,
            "HPTQ": tuple,
            "Wet": list,
            "Dry": list,
            "EffectBonus": float
        }
        failureFlag = False
        for terrainType in self.codex:
            terrainTypeInfo = self.codex.get(terrainType)
            for attribute in requiredAttrs:
                if attribute not in terrainTypeInfo:
                    print(f'Terrain Type: {terrainType} missing attribute: {attribute}')
                    failureFlag = True
                elif not isinstance(terrainTypeInfo.get(attribute), requiredAttrs.get(attribute)):
                    if isinstance(terrainTypeInfo.get(attribute), int) and requiredAttrs.get(attribute) == float:
                        pass
                    else:
                        print(f'Terrain Type: {terrainType}; Attribute: {attribute} is of type {type(terrainTypeInfo.get(attribute))} when it should be {requiredAttrs.get(attribute)}')
                        failureFlag = True
        if failureFlag:
            print("ERROR: Terrain Codex")
            raise CodexValidationException

    def getCodex(self): return self.codex


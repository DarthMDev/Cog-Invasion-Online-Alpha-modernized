"""

  Filename: GunGameLevelLoader.py
  Created by: blach (22Apr15)

"""

from panda3d.core import NodePath, Vec3, Point3, CompassEffect
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import OnscreenText

from lib.coginvasion.hood.SkyUtil import SkyUtil
from lib.coginvasion.distributed.HoodMgr import HoodMgr
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.dna.DNAParser import DNAStorage

hoodMgr = HoodMgr()

class GunGameLevelLoader:
    notify = directNotify.newCategory("GunGameLevelLoader")

    LevelData = {
        # momada means: Mix Of Mint And District Attorney's
        'momada': {
            'name': CIGlobals.ToonBattleOriginalLevel,
            'camera': (Point3(0.0, -25.80, 7.59), Vec3(0.00, 0.00, 0.00)),
            'models': [
                "phase_11/models/lawbotHQ/LB_Zone03a.bam",
                "phase_11/models/lawbotHQ/LB_Zone04a.bam",
                "phase_11/models/lawbotHQ/LB_Zone7av2.bam",
                "phase_11/models/lawbotHQ/LB_Zone08a.bam",
                "phase_11/models/lawbotHQ/LB_Zone13a.bam",
                "phase_10/models/cashbotHQ/ZONE17a.bam",
                "phase_10/models/cashbotHQ/ZONE18a.bam",
                "phase_11/models/lawbotHQ/LB_Zone22a.bam"
            ],
            'parents': [
                render,
                "EXIT",
                "EXIT",
                "EXIT",
                "ENTRANCE",
                "ENTRANCE",
                "ENTRANCE",
                "EXIT"
            ],
            'model_positions': [
                Point3(0.00, 0.00, 0.00),
                Point3(-1.02, 59.73, 0.00),
                Point3(0.00, 74.77, 0.00),
                Point3(0.00, 89.37, -13.50),
                Point3(16.33, -136.53, 0.00),
                Point3(-1.01, -104.40, 0.00),
                Point3(0.65, -23.86, 0.00),
                Point3(-55.66, -29.01, 0.00)
            ],
            'model_orientations': [
                Vec3(0.00, 0.00, 0.00),
                Vec3(0.00, 0.00, 0.00),
                Vec3(90.00, 0.00, 0.00),
                Vec3(180.00, 0.00, 0.00),
                Vec3(97.00, 0.00, 0.00),
                Vec3(359.95, 0.00, 0.00),
                Vec3(90.00, 0.00, 0.00),
                Vec3(270.00, 0.00, 0.00)
            ],
            'spawn_points': [
                (Point3(0, 0, 0), Vec3(0, 0, 0)),
                (Point3(-20, 50, 0), Vec3(0, 0, 0)),
                (Point3(20, 50, 0), Vec3(0, 0, 0)),
                (Point3(0, 120, 0), Vec3(0, 0, 0)),
                (Point3(0, 100, 0), Vec3(180, 0, 0)),
                (Point3(-90, 0, 0), Vec3(0, 0, 0)),
                (Point3(-170, 0, 0), Vec3(0, 0, 0)),
                (Point3(-90, 50, 0), Vec3(0, 0, 0)),
                (Point3(-170, 50, 0), Vec3(0, 0, 0)),
                (Point3(35, 250, 0), Vec3(-90, 0, 0)),
                (Point3(0, 285, 0), Vec3(180, 0, 0)),
                (Point3(-185, 250, 0), Vec3(90, 0, 0))
            ]
        },

        'dg': {
            'name': CIGlobals.DaisyGardens,
            'camera': (Point3(-33.13, -3.20, 48.62), Vec3(326.31, 332.68, 0.00)),
            'dna': [
                'phase_8/dna/storage_DG.dna',
                'phase_8/dna/storage_DG_sz.dna',
                'phase_8/dna/daisys_garden_sz.dna'
            ],
            'sky': 'TT',
            'spawn_points': hoodMgr.dropPoints[CIGlobals.DaisyGardens]
        },

        'mml': {
            'name': CIGlobals.MinniesMelodyland,
            'camera': (Point3(-54.42, -91.05, 34.89), Vec3(315.29, 336.80, 0.00)),
            'dna': [
                'phase_6/dna/storage_MM.dna',
                'phase_6/dna/storage_MM_sz.dna',
                'phase_6/dna/minnies_melody_land_sz.dna'
            ],
            'sky': 'MM',
            'spawn_points': hoodMgr.dropPoints[CIGlobals.MinniesMelodyland]
        },

        'cbhq': {
            'name': CIGlobals.CashbotHQ,
            'camera': (Point3(302.64, 5.00, 15.20), Vec3(135.00, 341.57, 0.00)),
            'model': 'phase_10/models/cogHQ/CashBotShippingStation.bam',
            'sky': None,
            'spawn_points': hoodMgr.dropPoints[CIGlobals.CashbotHQ]
        }
    }

    SkyData = {
        'TT': 'phase_3.5/models/props',
        'MM': 'phase_6/models/props',
        'cog': 'phase_9/models/cogHQ',

        'MovingSkies': ['TT']
    }

    def __init__(self):
        self.levelName = None
        self.dnaStore = DNAStorage()
        self.loadingText = None

        # for not momada only:
        self.levelGeom = None
        self.skyUtil = None
        self.skyModel = None

        # for momada only:
        self.momadaAreas = []
        self.momadaAreaName2areaModel = {}

    def setLevel(self, level):
        self.levelName = level

    def getLevel(self):
        return self.levelName

    def getCameraOfCurrentLevel(self):
        return self.LevelData[self.getLevel()]['camera']

    def getSpawnPoints(self):
        # Return the spawn points for this level.
        pointData = self.LevelData[self.levelName]['spawn_points']
        if self.levelName == "momada":
            return pointData
        else:
            # These points come from lib.coginvasion.distributed.HoodMgr,
            # which is a tuple of a bunch of arrays with pos as first
            # 3, and hpr as last 3 list elements.
            #
            # Disect the arrays and return a tuple holding a Point3 pos, and a Vec3 hpr.
            array = []
            for posAndHpr in pointData:
                array.append(
                    (
                        Point3(
                            posAndHpr[0],
                            posAndHpr[1],
                            posAndHpr[2]
                        ),

                        Vec3(
                            posAndHpr[3],
                            posAndHpr[4],
                            posAndHpr[5]
                        )
                    )
                )
            return array

    def getNameOfCurrentLevel(self):
        return self.LevelData[self.getLevel()]['name']

    def load(self):
        self.unload()
        if self.loadingText:
            self.loadingText.destroy()
            self.loadingText = None
        self.loadingText = OnscreenText(text = "Loading " + self.getNameOfCurrentLevel() + "...",
            font = CIGlobals.getMinnieFont(), fg = (1, 1, 1, 1))
        self.loadingText.setBin('gui-popup', 0)
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        if self.levelName == "momada":
            # momada is completely different from the other levels,
            # so it has it's own separate method for loading.
            self.__momadaLoad()
        elif self.levelName in ['cbhq']:
            # Cog hqs are just one model with everything in it. no dna loading needed.
            modelPath = self.LevelData[self.levelName]['model']
            self.levelGeom = loader.loadModel(modelPath)
            self.levelGeom.flattenMedium()
            self.levelGeom.reparentTo(render)
            if self.LevelData[self.levelName]['sky'] != None:
                self.skyModel = loader.loadModel(self.SkyData['cog'] + '/cog_sky.bam')
                self.skyUtil = SkyUtil()
                self.skyUtil.startSky(self.skyModel)
                self.skyModel.reparentTo(render)
        else:
            # It's a playground with dna and stuff. Just do the
            # normal loading procedure.
            dnaFiles = self.LevelData[self.levelName]['dna']
            skyType = self.LevelData[self.levelName]['sky']
            skyPhase = self.SkyData[skyType]
            loader.loadDNAFile(self.dnaStore, 'phase_4/dna/storage.dna')
            for index in range(len(dnaFiles)):
                if index == len(dnaFiles) - 1:
                    node = loader.loadDNAFile(self.dnaStore, dnaFiles[index])
                    if node.getNumParents() == 1:
                        self.levelGeom = NodePath(node.getParent(0))
                        self.levelGeom.reparentTo(hidden)
                    else:
                        self.levelGeom = hidden.attachNewNode(node)
                    self.levelGeom.flattenMedium()
                    gsg = base.win.getGsg()
                    if gsg:
                        self.levelGeom.prepareScene(gsg)
                    self.levelGeom.reparentTo(render)
                else:
                    loader.loadDNAFile(self.dnaStore, dnaFiles[index])
            self.skyModel = loader.loadModel(skyPhase + "/" + skyType + "_sky.bam")
            self.skyUtil = SkyUtil()
            self.skyUtil.startSky(self.skyModel)
            self.skyModel.reparentTo(camera)
            ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
            self.skyModel.node().setEffect(ce)
        if self.loadingText:
            self.loadingText.destroy()
            self.loadingText = None

    def __momadaLoad(self):

        def attachArea(itemNum):
            name = 'MomadaArea-%s' % itemNum
            area = self.momadaAreaName2areaModel.get(name)
            parents = self.LevelData['momada']['parents']
            parent = parents[itemNum]
            if type(parent) == type(""):
                parent = self.momadaAreas[itemNum - 1].find('**/' + parent)
            pos = self.LevelData['momada']['model_positions'][itemNum]
            hpr = self.LevelData['momada']['model_orientations'][itemNum]
            area.reparentTo(parent)
            area.setPos(pos)
            area.setHpr(hpr)

        _numItems = 0
        name = None
        for item in self.LevelData['momada']['models']:
            name = 'MomadaArea-%s' % _numItems
            area = loader.loadModel(item)
            self.momadaAreas.append(area)
            self.momadaAreaName2areaModel[name] = area
            attachArea(_numItems)
            _numItems += 1
            self.notify.info("Loaded and attached %s momada areas." % _numItems)

    def unload(self):
        if self.levelName == "momada":
            for area in self.momadaAreas:
                self.momadaAreas.remove(area)
                area.removeNode()
                del area
            self.momadaAreas = []
            self.momadaAreaName2areaModel = {}
        else:
            if self.skyUtil:
                self.skyUtil.stopSky()
                self.skyUtil = None
            if self.skyModel:
                self.skyModel.removeNode()
                self.skyModel = None
            if self.levelGeom:
                self.levelGeom.removeNode()
                self.levelGeom = None

    def cleanup(self):
        self.momadaAreas = None
        self.momadaAreaName2areaModel = None
        self.dnaStore.resetAll()
        self.dnaStore = None

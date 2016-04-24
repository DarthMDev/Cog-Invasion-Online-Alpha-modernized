# Filename: DistributedDodgeballGame.py
# Created by:  blach (18Apr16)
#
# OMG FINALLY THE DODGEBALL GAME!!

from panda3d.core import Fog, Point3, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon import ParticleLoader

from DistributedToonFPSGame import DistributedToonFPSGame
from DodgeballFirstPerson import DodgeballFirstPerson

class DistributedDodgeballGame(DistributedToonFPSGame):
    """The winter dodgeball minigame (client side)"""

    notify = directNotify.newCategory("DistributedDodgeballGame")

    TreeData = [['prop_snow_tree_small_ur', Point3(23.23, 66.52, 7.46)],
	            ['prop_snow_tree_small_ul', Point3(-34.03, 88.02, 24.17)],
	            ['prop_snow_tree_small_ur', Point3(-54.80, 0, 4.19)],
	            ['prop_snow_tree_small_ul', Point3(54.80, -5, 4.19)],
	            ['prop_snow_tree_small_ur', Point3(62.71, 62.66, 16.80)],
	            ['prop_snow_tree_small_ul', Point3(-23.23, -66.52, 6)],
	            ['prop_snow_tree_small_ur', Point3(34.03, -88.02, 23)],
	            ['prop_snow_tree_small_ul', Point3(-62.71, -62.66, 16)]]

    GameSong = "phase_4/audio/bgm/MG_Dodgeball.mp3"
    GameDesc = ("Welcome to the north! You have been invited to play dodgeball with the penguins!\n\n"
                "How To Play\nWASD to Move and use the mouse to aim.\nLeft click to Throw!\nRight click"
                " to Catch!\n\nObjective\nThe first team to get everyone out wins!")

    InitCamTrans = [Point3(42.8565, 75.438, 19.5317), Vec3(154.001, -8.27901, 0)]

    def __init__(self, cr):
        try:
            self.DistributedDodgeballGame_initialized
            return
        except:
            self.DistributedDodgeballGame_initialized = 1

        DistributedToonFPSGame.__init__(self, cr)

        self.firstPerson = DodgeballFirstPerson(self)

        # Environment vars
        self.sky = None
        self.arena = None
        self.fog = None
        self.snow = None
        self.snowRender = None
        self.trees = []

    def __getSnowTree(self, path):
        trees = loader.loadModel('phase_8/models/props/snow_trees.bam')
        tree = trees.find('**/' + path)
        tree.find('**/*shadow*').removeNode()
        return tree

    def load(self):
        self.setMinigameMusic(DistributedDodgeballGame.GameSong)
        self.setDescription(DistributedDodgeballGame.GameDesc)
        self.createWorld()

        trans = DistributedDodgeballGame.InitCamTrans
        camera.setPos(trans[0])
        camera.setHpr(trans[1])

        DistributedToonFPSGame.load(self)

    def createWorld(self):
        self.deleteWorld()

        self.sky = loader.loadModel("phase_3.5/models/props/BR_sky.bam")
        self.sky.reparentTo(render)
        self.sky.setZ(-5)
        self.sky.setFogOff()

        self.arena = loader.loadModel("phase_4/models/minigames/dodgeball_arena.egg")
        self.arena.reparentTo(render)
        self.arena.find('**/team_divider').setBin('ground', 18)
        self.arena.find('**/floor').setBin('ground', 18)
        self.arena.find('**/team_divider_coll').setCollideMask(CIGlobals.FloorBitmask)

        for data in DistributedDodgeballGame.TreeData:
            code = data[0]
            pos = data[1]
            tree = self.__getSnowTree(code)
            tree.reparentTo(render)
            tree.setPos(pos)
            self.trees.append(tree)

        self.snow = ParticleLoader.loadParticleEffect('phase_8/etc/snowdisk.ptf')
        self.snow.setPos(0, 0, 5)
        self.snowRender = self.arena.attachNewNode('snowRender')
        self.snowRender.setDepthWrite(0)
        self.snowRender.setBin('fixed', 1)
        self.snow.start(camera, self.snowRender)

        self.fog = Fog('snowFog')
        self.fog.setColor(0.486, 0.784, 1)
        self.fog.setExpDensity(0.003)
        render.setFog(self.fog)

    def deleteWorld(self):
        for tree in self.trees:
            tree.removeNode()
        self.trees = []
        if self.snow:
            self.snow.cleanup()
            self.snow = None
        if self.snowRender:
            self.snowRender.removeNode()
            self.snowRender = None
        self.fog = None
        if self.sky:
            self.sky.removeNode()
            self.sky = None
        if self.arena:
            self.arena.removeNode()
            self.arena = None
        render.clearFog()

    def announceGenerate(self):
        DistributedToonFPSGame.announceGenerate(self)
        self.load()

    def disable(self):
        self.deleteWorld()
        self.trees = None
        if self.firstPerson:
            self.firstPerson.cleanup()
            self.firstPerson = None
        DistributedToonFPSGame.disable(self)

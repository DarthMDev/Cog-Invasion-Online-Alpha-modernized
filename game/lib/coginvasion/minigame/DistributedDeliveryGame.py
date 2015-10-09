# Filename: DistributedDeliveryGame.py
# Created by:  blach (04Oct15)

from panda3d.core import CompassEffect, NodePath

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.minigame.DistributedMinigame import DistributedMinigame
from lib.coginvasion.hood.SkyUtil import SkyUtil

class DistributedDeliveryGame(DistributedMinigame):
    notify = directNotify.newCategory('DistributedDeliveryGame')

    def __init__(self, cr):
        DistributedMinigame.__init__(self, cr)
        self.world = None
        self.gagShop = None
        self.sky = None
        self.skyUtil = SkyUtil()
        base.localAvatar.hasBarrel = False
        self.soundPickUpBarrel = None
        self.soundDropOff = None
        self.barrelsByAvId = {}

    def giveBarrelToSuit(self, suitId):
        suit = self.cr.doId2do.get(suitId)
        if suit:
            barrel = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
            barrel.reparentTo(suit.find('**/joint_Rhold'))
            #barrel.setP(90)
            #barrel.setZ(0.25)
            barrel.setScale(0.2)
            barrel.find('**/gagTankColl').removeNode()
            self.barrelsByAvId[suitId] = barrel

    def giveBarrelToPlayer(self, avId):
        if avId == self.localAvId:
            if not base.localAvatar.hasBarrel:
                base.localAvatar.hasBarrel = True
                base.playSfx(self.soundPickUpBarrel)
            else:
                return
        av = self.cr.doId2do.get(avId)
        if av:
            av.setForcedTorsoAnim('catchneutral')
            barrel = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
            barrel.reparentTo(av.find('**/def_joint_right_hold'))
            barrel.setP(90)
            barrel.setZ(0.25)
            barrel.setScale(0.2)
            barrel.find('**/gagTankColl').removeNode()
            self.barrelsByAvId[avId] = barrel

    def dropOffBarrel(self, avId):
        if avId == self.localAvId:
            if base.localAvatar.hasBarrel:
                base.localAvatar.hasBarrel = False
                base.playSfx(self.soundDropOff)
            else:
                return
        av = self.cr.doId2do.get(avId)
        if av:
            av.clearForcedTorsoAnim()
            barrel = self.barrelsByAvId.get(avId)
            if barrel != None or not barrel.isEmpty():
                barrel.removeNode()
                del self.barrelsByAvId[avId]

    def load(self):
        self.soundPickUpBarrel = base.loadSfx('phase_6/audio/sfx/SZ_MM_gliss.mp3')
        self.soundDropOff = base.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bell_for_trolley.mp3')
        self.setMinigameMusic('phase_4/audio/bgm/MG_Delivery.mp3')
        self.setDescription('A new supply of Gags were just shipped to Toontown! ' + \
            'Run over to a truck with Gag barrels to take a barrel out. Then, carry it over to the Gag Shop. ' + \
            'Try to unload and deliver as many barrels as you can to the Gag Shop. ' + \
            'Watch out for the Cogs - they might try to snatch a barrel!')
        self.setWinnerPrize(100)
        self.setLoserPrize(0)
        self.gagShop = loader.loadModel('phase_4/models/modules/gagShop_TT.bam')
        self.gagShop.reparentTo(base.render)
        self.gagShop.setY(-70)
        self.world = loader.loadModel('phase_4/models/minigames/delivery_area.egg')
        self.world.setY(-5)
        self.world.reparentTo(base.render)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky.bam')
        self.sky.reparentTo(base.camera)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)
        self.sky.setZ(-20)
        self.skyUtil.startSky(self.sky)
        base.camera.setPos(20, 50, 30)
        base.camera.lookAt(20, 0, 7.5)
        DistributedMinigame.load(self)

    def enterStart(self):
        DistributedMinigame.enterStart(self)
        beepSound = base.loadSfx('phase_4/audio/sfx/MG_delivery_truck_beep.mp3')
        base.playSfx(beepSound)

    def enterPlay(self):
        DistributedMinigame.enterPlay(self)
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.enableAvatarControls()

    def exitPlay(self):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.detachCamera()
        DistributedMinigame.exitPlay(self)

    def announceGenerate(self):
        DistributedMinigame.announceGenerate(self)
        self.load()

    def disable(self):
        if self.world:
            self.world.removeNode()
            self.world = None
        if self.gagShop:
            self.gagShop.removeNode()
            self.gagShop = None
        if self.sky:
            self.sky.removeNode()
            self.sky = None
        self.skyUtil = None
        self.soundPickUpBarrel = None
        self.soundDropOff = None
        del base.localAvatar.hasBarrel
        self.barrelsByAvId = None
        DistributedMinigame.disable(self)

# Filename: FactorySneakWorld.py
# Created by:  blach (20Aug15)

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State

from FactorySneakJellybeanBarrel import FactorySneakJellybeanBarrel
from FactorySneakPlayer import FactorySneakPlayer
from FactorySneakGuardSuit import FactorySneakGuardSuit
import CogGuardGlobals as CGG

class FactorySneakWorld(DirectObject):
    notify = directNotify.newCategory("FactorySneakWorld")

    WORLD_MODEL_PATH = "phase_9/models/cogHQ/SelbotLegFactory.bam"
    BAD_SECTIONS = ['ZONE12', 'ZONE30', 'ZONE31', 'ZONE32', 'ZONE33', 'ZONE34',
        'ZONE35', 'ZONE36', 'ZONE37', 'ZONE38', 'ZONE60', 'ZONE61']

    COLLECTED_BARREL_EVENT = "CollectedJBSBarrel"
    GUARD_SHOT_EVENT = "GuardShot"

    def __init__(self, mg):
        DirectObject.__init__(self)
        self.mg = mg
        self.worldMdl = None
        self.occluderData = None
        self.barrels = []
        self.guards = []
        self.player = FactorySneakPlayer(mg)

    def setupPlayer(self):
        self.player.setupInterface()
        self.player.spawn()
        self.player.startFPS(enableLookAround = False)
        self.accept(self.GUARD_SHOT_EVENT, self.__handleGuardShot)

    def __handleGuardShot(self, guard, dmg):
        guard.setHealth(guard.getHealth() - dmg)
        guard.updateHealthBar(guard.getHealth())
        if guard.getHealth() < 1:
            guard.dead()
        else:
            guard.shot()

    def enablePlayerControls(self):
        self.player.enableLookAround()
        self.player.enableControls()
        self.accept('control', self.crouch)
        self.accept('control-up', self.uncrouch)

    def crouch(self):
        pass

    def uncrouch(self):
        pass

    def disablePlayerControls(self):
        self.player.disableControls()
        self.player.disableLookAround()

    def cleanup(self):
        self.ignore(self.GUARD_SHOT_EVENT)
        self.deleteJellybeanBarrels()
        self.unloadWorld()
        self.deleteGuards()
        self.barrels = None
        self.guards = None
        self.mg = None

    def makeGuard(self, key):
        guard = FactorySneakGuardSuit(self, key)
        guard.reparentTo(base.render)
        guard.generate()
        self.guards.append(guard)

    def deleteGuard(self, guard):
        if guard in self.guards:
            self.guards.remove(guard)
            guard.disable()
            guard.delete()

    def makeGuards(self):
        for key in CGG.FactoryGuardPoints.keys():
            self.makeGuard(key)

    def deleteGuards(self):
        for guard in self.guards:
            self.deleteGuard(guard)

    def createJellybeanBarrel(self, i):
        jellybeanBarrel = FactorySneakJellybeanBarrel(self)
        jellybeanBarrel.loadBarrel()
        jellybeanBarrel.request('Available')
        jellybeanBarrel.reparentTo(base.render)
        pos, hpr = CGG.JellybeanBarrelPoints[i]
        jellybeanBarrel.setPos(pos)
        jellybeanBarrel.setHpr(hpr)
        self.barrels.append(jellybeanBarrel)

    def deleteJellybeanBarrel(self, barrel):
        if (barrel in self.barrels):
            self.barrels.remove(barrel)
            barrel.cleanup()

    def loadJellybeanBarrels(self):
        for i in xrange(len(CGG.JellybeanBarrelPoints)):
            self.createJellybeanBarrel(i)

    def deleteJellybeanBarrels(self):
        for barrel in self.barrels:
            barrel.cleanup()
        self.barrels = []

    def loadWorld(self):
        self.unloadWorld()

        self.worldMdl = base.loader.loadModel(self.WORLD_MODEL_PATH)
        for sectionName in self.BAD_SECTIONS:
            sectionNode = self.worldMdl.find('**/' + sectionName)
            if (not sectionNode.isEmpty()):
                sectionNode.removeNode()
        self.occluderData = base.loader.loadModel("factory_sneak_occluders.egg")
        for occluderNode in self.occluderData.findAllMatches('**/+OccluderNode'):
            base.render.setOccluder(occluderNode)
            occluderNode.node().setDoubleSided(True)

    def unloadWorld(self):
        if (self.worldMdl != None):
            self.worldMdl.removeNode()
            self.worldMdl = None
        if self.occluderData != None:
            self.occluderData.removeNode()
            self.occluderData = None

    def showWorld(self):
        self.worldMdl.reparentTo(base.render)

    def hideWorld(self):
        self.worldMdl.reparentTo(base.hidden)

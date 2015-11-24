# Filename: DistributedGunGameFlag.py
# Created by:  blach (21Nov15)

from panda3d.core import CollisionSphere, CollisionNode, NodePath

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNode import DistributedNode

from lib.coginvasion.globals import CIGlobals
import GunGameGlobals as GGG

class DistributedGunGameFlag(DistributedNode):
    notify = directNotify.newCategory('DistributedGunGameFlag')
    colors = {GGG.Teams.RED: (1, 0, 0, 1.0),  GGG.Teams.BLUE: (0, 0, 1, 1.0)}
    pole_color = (0.1, 0.1, 0.1, 1.0)
    torsoType2flagY = {"dgs_shorts": -1.5, "dgs_skirt": -1.5, "dgm_shorts": -1.1,
                       "dgm_skirt": -1.1, "dgl_shorts": -1.1, "dgl_skirt": -1.1}

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'dggflag')
        self.flagMdl = None
        self.team = None
        self.collNP = None
        self.flagCollNP = None

    def acceptPointCollisions(self):
        self.acceptOnce('enter' + self.uniqueName('flagpoint_colnode'), self.__touchedFlagPointSphere)

    def __touchedFlagPointSphere(self, entry):
        self.sendUpdate('requestDropOff')

    def dropOffFlag(self, avId):
        if base.minigame.team != self.team:
            if avId != base.localAvatar.doId:
                base.minigame.showAlert("Your team has captured the enemy's flag!")
            else:
                base.minigame.showAlert("You have captured the enemy's flag!")
                base.minigame.localAvHasFlag = False
        else:
            base.minigame.showAlert("The enemy has captured your flag!")

    def setTeam(self, team):
        # The team this flag is associated with.
        self.team = team

    def getTeam(self):
        return self.team

    def placeAtMainPoint(self):
        pos, hpr = base.minigame.loader.getFlagPoint(self.team)
        self.flagCollNP.unstash()
        self.flagMdl.reparentTo(render)
        self.flagMdl.setPos(pos)
        self.flagMdl.setHpr(hpr)
        if base.minigame.team != self.team:
            self.acceptOnce('enter' + self.uniqueName('flag_colnode'), self.__touchedFlagSphere)

    def __touchedFlagSphere(self, entry):
        self.sendUpdate('requestPickup')

    def pickupFlag(self, avId):
        av = base.minigame.getRemoteAvatar(avId)
        if av:
            if self.team == base.minigame.team:
                base.minigame.showAlert("The enemy has your flag!")
            else:
                if avId != base.localAvatar.doId:
                    base.minigame.showAlert("Your team has the enemy's flag!")
                else:
                    base.minigame.showAlert("You have the enemy's flag!")
                    base.minigame.localAvHasFlag = True
                    self.acceptPointCollisions()
            self.flagCollNP.stash()
            self.ignore('enter' + self.uniqueName('flag_colnode'))
            self.flagMdl.reparentTo(av.avatar.find('**/def_joint_attachFlower'))
            self.flagMdl.setPos(0.2, self.torsoType2flagY[av.avatar.getTorso()], -1)
            self.flagMdl.setHpr(0, 0, 0)

    def dropFlag(self, x, y, z):
        base.minigame.localAvHasFlag = False
        self.flagCollNP.unstash()
        if base.minigame.team != self.team:
            self.acceptOnce('enter' + self.uniqueName('flag_colnode'), self.__touchedFlagSphere)
            base.minigame.showAlert("Your team has dropped the enemy's flag!")
        else:
            base.minigame.showAlert("The enemy has dropped your flag!")
        self.flagMdl.reparentTo(render)
        self.flagMdl.setPos(x, y, z)

    def b_dropFlag(self, x, y, z):
        self.sendUpdate('dropFlag', [x, y, z])
        self.dropFlag(x, y, z)

    def flagReturned(self):
        if base.minigame.team != self.team:
            base.minigame.showAlert("The enemy's flag has returned!")
        else:
            base.minigame.showAlert("Your flag has returned!")

    def announceGenerate(self):
        self.reparentTo(render)
        base.minigame.flags.append(self)
        self.flagMdl = loader.loadModel('phase_4/models/minigames/flag.egg')
        self.flagMdl.reparentTo(render)
        self.flagMdl.find('**/flag').setTwoSided(1)
        self.flagMdl.find('**/flag_pole').setColor(self.pole_color)
        self.flagMdl.find('**/flag').setColor(self.colors[self.team])
        sphere = CollisionSphere(0, 0, 0, 4)
        sphere.setTangible(0)
        node = CollisionNode(self.uniqueName('flagpoint_colnode'))
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.collNP = self.attachNewNode(node)
        sphere = CollisionSphere(0, 0, 0, 2)
        sphere.setTangible(0)
        node = CollisionNode(self.uniqueName('flag_colnode'))
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.flagCollNP = self.flagMdl.attachNewNode(node)
        pos, hpr = base.minigame.loader.getFlagPoint_Point(self.team)
        self.setPos(pos)
        self.setHpr(hpr)

    def disable(self):
        if self.flagMdl:
            self.flagMdl.removeNode()
            self.flagMdl = None
        if self.collNP:
            self.collNP.removeNode()
            self.collNP = None
        self.team = None
        DistributedNode.disable(self)

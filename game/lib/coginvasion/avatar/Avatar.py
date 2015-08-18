"""

  Filename: Avatar.py
  Created by: blach (??July14)

"""

#from libccoginvasion import LabelScaler

from direct.actor.Actor import Actor
from direct.showbase.ShadowDemo import ShadowCaster, arbitraryShadow
from panda3d.core import *
from pandac.PandaModules import *
from direct.directnotify.DirectNotify import DirectNotify
from lib.coginvasion.toon.ChatBalloon import ChatBalloon
from lib.coginvasion.toon.LabelScaler import LabelScaler
from lib.coginvasion.toon.NameTag import NameTag
from lib.coginvasion.base.ShadowPlacer import ShadowPlacer
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon import ToonTalker
from direct.controls.ControlManager import CollisionHandlerRayStart
import random

notify = DirectNotify().newCategory("Avatar")

class Avatar(ToonTalker.ToonTalker, Actor):

    def __init__(self, mat=0):
        self.mat = mat
        self.name = ''
        self.chat = ''
        try:
            self.Avatar_initialized
            return
        except:
            self.Avatar_initialized = 1

        ToonTalker.ToonTalker.__init__(self)
        Actor.__init__(self, None, None, None, flattenable=0, setFinal=1)#self.setColorOff()

        self.nameTag = None
        self.setTwoSided(False)

        self.avatarType = None
        self.charName = None
        self.name = None
        self.tag = None
        self.height = 0
        return

    def deleteNameTag(self):
        if self.nameTag:
            self.nameTag.destroy()
            self.nameTag = None

    def disable(self):
        try:
            self.Avatar_disabled
        except:
            self.Avatar_disabled = 1
            self.deleteShadow()
            self.deleteNameTag()
            self.removeLoopTask()
            self.mat = None
            self.tag = None
            self.chat = None
            self.height = None
            self.avatarType = None
            self.charName = None
            self.nameTag = None
            self.name = None
            Actor.cleanup(self)

    def delete(self):
        try:
            self.Avatar_deleted
        except:
            self.Avatar_deleted = 1
            self.removeLoopTask()
            Actor.delete(self)

    def getNameTag(self):
        return self.nameTag.getNodePath()

    def setHeight(self, height):
        self.height = height

    def getHeight(self):
        return self.height

    def setChat(self, chatString = None):
        ToonTalker.ToonTalker.setChatAbsolute(self, chatString)

    def setName(self, nameString = None, avatarType = None, charName = None, createNow = 0):
        if not nameString:
            return
        self.name = nameString
        if charName:
            self.charName = charName
        if createNow:
            self.setupNameTag()

    def getName(self):
        return self.name

    def setupNameTag(self, tempName = None):
        if not self.name and not tempName:
            return
        offset = 0.0
        if self.avatarType:
            if self.avatarType == CIGlobals.Suit:
                if self.charName:
                    offset = 0.5
                    z = CIGlobals.SuitNameTagPos[self.charName]
            elif self.avatarType == CIGlobals.CChar:
                z = 5
            elif self.avatarType == CIGlobals.Toon:
                offset = 0.5
            else:
                z = 0

        self.deleteNameTag()
        if tempName:
            name = tempName
        else:
            name = self.name
        tag = NameTag(name, self.avatarType)
        tag.setTextColor(tag.NameTagColors[self.avatarType]["fg"])

        self.nameTag = tag
        np = tag.getNodePath()
        np.setEffect(BillboardEffect.make(Vec3(0,0,1), True, False, 3.0, camera, Point3(0,0,0)))

        ToonTalker.ToonTalker.setAvatar(self, self, np)

        np.reparentTo(self)
        if self.avatarType == CIGlobals.Toon:
            np.setZ(self.getHeight() + offset)
            self.nameTag.setClickable(1)
        elif self.avatarType == CIGlobals.Suit or self.avatarType == CIGlobals.CChar:
            np.setZ(z + offset)

        if self.avatarType == CIGlobals.Suit:
            self.nameTag.setFont(CIGlobals.getSuitFont())
        else:
            self.nameTag.setFont(CIGlobals.getToonFont())

        ls = LabelScaler()
        ls.resize(np)

    def getAirborneHeight(self):
        height = self.getPos(self.shadowPlacer.shadowNodePath)
        return height.getZ() + 0.025

    def initializeBodyCollisions(self, collIdStr, height, radius):
        if hasattr(self, 'collNodePath'):
            if self.collNodePath:
                self.notify.info('Tried to initialize body collisions more than once!')
                return
        cTube = CollisionTube(0, 0, height, 0, 0, 0, radius)
        cNode = CollisionNode('cNode')
        cNode.addSolid(cTube)
        cNode.setCollideMask(CIGlobals.WallBitmask)
        self.collNodePath = self.attachNewNode(cNode)
        #self.collNodePath.show()

    def collisionFix(self, task):
        self.collNodePath.forceRecomputeBounds()
        return task.cont

    def initializeRay(self, name, radius):
        if hasattr(self, 'rayNodePath'):
            if self.rayNodePath:
                self.notify.warning('Tried to initialize ray collisions more than once!')
                return

        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        cRayNode = CollisionNode(name + 'r')
        cRayNode.addSolid(cRay)
        self.cRayNodePath = self.attachNewNode(cRayNode)
        cRayBitMask = CIGlobals.FloorBitmask
        cRayNode.setFromCollideMask(cRayBitMask)
        cRayNode.setIntoCollideMask(BitMask32.allOff())
        lifter = CollisionHandlerFloor()
        lifter.addCollider(self.cRayNodePath, self)

        cSphere = CollisionSphere(0.0, 0.0, radius, 0.01)
        cSphereNode = CollisionNode(name + 'fc')
        cSphereNode.addSolid(cSphere)
        cSphereNodePath = self.attachNewNode(cSphereNode)
        #cSphereNodePath.show()

        cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
        cSphereNode.setIntoCollideMask(BitMask32.allOff())

        pusher = CollisionHandlerPusher()
        pusher.addCollider(cSphereNodePath, self)
        self.floorCollNodePath = cSphereNodePath
        base.cTrav.addCollider(self.floorCollNodePath, pusher)
        base.shadowTrav.addCollider(self.cRayNodePath, lifter)

    def disableRay(self):
        if hasattr(self, 'cRayNodePath'):
            base.shadowTrav.removeCollider(self.cRayNodePath)
            self.cRayNodePath.removeNode()
            del self.cRayNodePath
            base.cTrav.removeCollider(self.floorCollNodePath)
            self.floorCollNodePath.removeNode()
            del self.floorCollNodePath
        self.rayNode = None

    def initializeLocalCollisions(self, senRadius, senZ, name):
        self.collNodePath.setCollideMask(BitMask32(0))
        self.collNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)

        pusher = CollisionHandlerPusher()
        pusher.setInPattern("%in")
        pusher.addCollider(self.collNodePath, self)

        base.cTrav.addCollider(self.collNodePath, pusher)

        collisionSphere = CollisionSphere(0, 0, 0, senRadius)
        sensorNode = CollisionNode(name + "s")
        sensorNode.addSolid(collisionSphere)
        self.sensorNodePath = self.attachNewNode(sensorNode)
        self.sensorNodePath.setZ(senZ)
        self.sensorNodePath.setCollideMask(BitMask32(0))
        self.sensorNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)

        event = CollisionHandlerEvent()
        event.setInPattern("%fn-into")
        event.setOutPattern("%fn-out")
        base.cTrav.addCollider(self.sensorNodePath, event)

    def stashBodyCollisions(self):
        if hasattr(self, 'collNodePath'):
            self.collNodePath.stash()

    def unstashBodyCollisions(self):
        if hasattr(self, 'collNodePath'):
            self.collNodePath.unstash()

    def stashRay(self):
        if hasattr(self, 'rayNodePath'):
            self.rayNodePath.stash()

    def unstashRay(self):
        if hasattr(self, 'rayNodePath'):
            self.rayNodePath.unstash()

    def disableBodyCollisions(self):
        self.notify.info('Disabling body collisions')
        if hasattr(self, 'collNodePath'):
            taskMgr.remove(self.uniqueName('collisionFixTask'))
            self.collNodePath.removeNode()
            del self.collNodePath
        return

    def deleteLocalCollisions(self):
        self.notify.info('Deleting local collisions!')
        base.cTrav.removeCollider(self.rayNodePath)
        base.cTrav.removeCollider(self.sensorNodePath)
        self.rayNodePath.remove_node()
        self.sensorNodePath.remove_node()

    def setAvatarScale(self, scale):
        self.getGeomNode().setScale(scale)

    def getShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                return self.shadow
        return None

    def initShadow(self):
        #self.shadow = arbitraryShadow(self.getGeomNode())

        self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
        self.shadow.setScale(CIGlobals.ShadowScales[self.avatarType])
        self.shadow.flattenMedium()
        self.shadow.setBillboardAxis(4)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        self.shadowPlacer = ShadowPlacer(self.shadow, self.mat)
        if self.avatarType == CIGlobals.Toon:
            self.shadow.reparentTo(self.getPart('legs').find('**/joint_shadow'))
        elif self.avatarType == CIGlobals.Suit:
            self.shadow.reparentTo(self)#.find('**/joint_shadow'))
        else:
            self.shadow.reparentTo(self)

    def deleteShadow(self):
        if hasattr(self, 'shadow'):
            if self.shadow:
                self.shadowPlacer.delete_shadow_ray()
                self.shadowPlacer = None
                self.shadow.removeNode()
                self.shadow = None
                #self.shadow.clear()
                #self.shadow = None

    def disableShadowRay(self):
        self.shadowPlacer.delete_shadow_ray()

    def enableShadowRay(self):
        self.shadowPlacer.setup_shadow_ray(self.shadow, self.mat)

    def loopFromFrameToZero(self, animName, restart = 1, partName = None, fromFrame = None):
        """
        Loop an animation from a frame, restarting at 0.
        This is only used in Make A Toon, but could be used in other things,
        that are not distributed.
        """
        dur = self.getDuration(animName, fromFrame = fromFrame)
        self.play(animName, partName = partName, fromFrame = fromFrame)
        if hasattr(self, 'cr'):
            taskName = self.cr.uniqueName('loopTask')
        else:
            taskName = 'loopTask'
        taskMgr.doMethodLater(
            dur, self.loopTask, taskName,
            extraArgs = [animName, restart, partName],
            appendTask = True
        )

    def removeLoopTask(self):
        if hasattr(self, 'cr'):
            taskMgr.remove(self.cr.uniqueName('loopTask'))
        else:
            taskMgr.remove('loopTask')

    def removePart(self, partName, lodName = "lodRoot"):
        self.removeLoopTask()
        Actor.removePart(self, partName, lodName = lodName)

    def loopTask(self, animName, restart, partName, task):
        self.loop(animName, restart, partName)
        return task.done

    def loop(self, animName, restart = 1, partName = None, fromFrame = None, toFrame = None):
        return Actor.loop(self, animName, restart, partName, fromFrame, toFrame)

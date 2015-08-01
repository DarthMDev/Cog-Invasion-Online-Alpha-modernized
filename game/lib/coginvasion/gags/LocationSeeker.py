"""

  Filename: LocationSeeker.py
  Created by: DecodedLogic (24Jul15)

"""

from panda3d.core import CollisionNode, CollisionRay, CollisionHandlerQueue
from lib.coginvasion.globals import CIGlobals
from direct.task.Task import Task

class LocationSeeker:

    def __init__(self, avatar, minDistance, maxDistance):
        self.dropShadowPath = 'phase_3/models/props/square_drop_shadow.bam'
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.mp3'
        self.moveShadowTaskName = 'Move Shadow'
        self.locationSelectedName = 'Location Selected'
        self.dropShadow = None
        self.rejectSfx = loader.loadSfx(self.rejectSoundPath)
        self.avatar = avatar
        self.cameraNode = None
        self.cameraRay = None
        self.cameraNP = None
        self.minDistance = minDistance
        self.maxDistance = maxDistance

    def startSeeking(self):
        if not self.dropShadow:
            self.buildShadow()

        # Let's setup the drop shadow's initial position.
        x, y, z = self.avatar.getPos(render)
        self.dropShadow.reparentTo(render)
        self.dropShadow.setPos(x, y + 5, z + 2)

        # Let's setup the collisions for the mouse.
        self.cameraNode = CollisionNode('coll_camera')
        self.cameraNode.setFromCollideMask(CIGlobals.WallBitmask)
        self.cameraRay = CollisionRay()
        self.cameraNode.addSolid(self.cameraRay)
        self.cameraNP = camera.attachNewNode(self.cameraNode)
        base.cTrav.addCollider(self.cameraNP, CollisionHandlerQueue())
        base.taskMgr.add(self.__moveShadow, self.moveShadowTaskName)
        self.avatar.acceptOnce('mouse1', self.locationChosen)

    def __moveShadow(self, task):
        if base.mouseWatcherNode.hasMouse():
            def PointAtZ(z, point, vec):
                if vec.getZ() != 0:
                    return point + vec * ((z-point.getZ()) / vec.getZ())
                else:
                    return self.getLocation()
            mouse = base.mouseWatcherNode.getMouse()
            self.cameraRay.setFromLens(base.camNode, mouse.getX(), mouse.getY())
            nearPoint = render.getRelativePoint(camera, self.cameraRay.getOrigin())
            nearVec = render.getRelativeVector(camera, self.cameraRay.getDirection())
            self.dropShadow.setPos(PointAtZ(.5, nearPoint, nearVec))
            self.dropShadow.setZ(base.localAvatar.getPos(render).getZ() + 0.5)
        return Task.cont

    def locationChosen(self):
        distance = self.avatar.getDistance(self.dropShadow)
        x, y, z = self.getLocation()
        if distance >= self.minDistance and distance <= self.maxDistance:
            self.avatar.sendUpdate('setDropLoc', [x, y, z])
            messenger.send(self.locationSelectedName)
        else:
            self.rejectSfx.play()
            self.avatar.acceptOnce('mouse1', self.locationChosen)

    def buildShadow(self):
        self.cleanupShadow()
        self.dropShadow = loader.loadModel(self.dropShadowPath)

    def getLocation(self):
        if self.dropShadow:
            return self.dropShadow.getPos(render)
        return self.avatar.getPos(render)

    def getLocationSelectedName(self):
        return self.locationSelectedName

    def cleanupShadow(self):
        if self.dropShadow:
            self.dropShadow.removeNode()
            self.dropShadow = None
            if self.cameraNode:
                self.cameraNP.removeNode()
                self.cameraNP = None
                self.cameraNode = None
                self.cameraRay = None

    def cleanup(self):
        base.taskMgr.remove(self.moveShadowTaskName)
        self.avatar.ignore('mouse1')
        self.cleanupShadow()
        self.rejectSfx.stop()
        self.rejectSfx = None
        self.avatar = None
        self.dropShadowPath = None
        self.rejectSoundPath = None
        self.locationSelectedName = None
        self.moveShadowTaskName = None

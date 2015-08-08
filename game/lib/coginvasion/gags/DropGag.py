"""

  Filename: DropGag.py
  Created by: DecodedLogic (16Jul15)

"""

from lib.coginvasion.gags.Gag import Gag
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.gags.GagState import GagState
from lib.coginvasion.globals import CIGlobals
from LocationSeeker import LocationSeeker
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func, SoundInterval, Wait, LerpScaleInterval
from panda3d.core import CollisionNode, CollisionHandlerEvent, CollisionHandlerFloor, CollisionSphere, BitMask32, Point3
import abc

class DropGag(Gag):
    notify = directNotify.newCategory('DropGag')

    def __init__(self, name, model, anim, damage, hitSfx, missSfx, scale, playRate):
        Gag.__init__(self, name, model, damage, GagType.DROP, hitSfx, anim = anim, playRate = playRate, scale = scale, autoRelease = True)
        self.missSfx = None
        self.buttonSoundPath = 'phase_5/audio/sfx/AA_drop_trigger_box.mp3'
        self.fallSoundPath = 'phase_5/audio/sfx/incoming_whistleALT.mp3'
        self.fallSoundInterval = None
        self.buttonSfx = None
        self.fallSfx = None
        self.button = None
        self.buttonAnim = 'push-button'
        self.moveShadowTaskName = 'Move Shadow'
        self.lHandJoint = None
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.collHandlerF = CollisionHandlerFloor()
        self.fallDuration = 0.75
        self.tButtonPress = 2.44
        self.isDropping = False
        self.locationSeeker = None
        self.dropLoc = None
        if game.process == 'client':
            self.missSfx = base.audio3d.loadSfx(missSfx)
            self.buttonSfx = base.audio3d.loadSfx(self.buttonSoundPath)
            self.fallSfx = base.audio3d.loadSfx(self.fallSoundPath)

    def buildButton(self):
        self.cleanupButton()
        self.button = loader.loadModel('phase_3.5/models/props/button.bam')

    def cleanupButton(self):
        if self.button:
            self.button.removeNode()

    def completeDrop(self):
        self.isDropping = False
        if game.process != 'client': return
        numFrames = base.localAvatar.getNumFrames(self.buttonAnim)
        ActorInterval(self.avatar, self.buttonAnim, startFrame = self.completeFrame, endFrame = numFrames,
                      playRate = self.playRate).start()
        self.reset()
        self.cleanupButton()
        if base.localAvatar == self.avatar:
            base.localAvatar.enablePieKeys()

    def setEndPos(self, x, y, z):
        self.dropLoc = Point3(x, y, z)

    def start(self):
        super(DropGag, self).start()
        self.buildButton()
        if not self.lHandJoint:
            self.lHandJoint = self.avatar.find('**/def_joint_left_hold')
        self.button.reparentTo(self.lHandJoint)
        track = Sequence(ActorInterval(self.avatar, self.buttonAnim, startFrame = 0, endFrame = self.chooseLocFrame,
                                       playRate = self.playRate))
        if self.isLocal():
            self.locationSeeker = LocationSeeker(self.avatar, 10, 50)
            self.avatar.acceptOnce(self.locationSeeker.getLocationSelectedName(), base.localAvatar.releaseGag)
            track.append(Func(self.locationSeeker.startSeeking))
        track.start()

    def unEquip(self):
        self.cleanupLocationSeeker()
        super(DropGag, self).unEquip()
        if self.state != GagState.LOADED:
            self.completeDrop()

    def buildCollisions(self):
        gagSph = CollisionSphere(0, 1.5, 0, 2)
        gagSensor = CollisionNode('gagSensor')
        gagSensor.addSolid(gagSph)
        sensorNP = self.gag.attachNewNode(gagSensor)
        sensorNP.setCollideMask(BitMask32(0))
        sensorNP.node().setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)
        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.add_collider(sensorNP, event)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def onCollision(self, entry):
        if not self.gag:
            return
        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        hitCog = False
        self.fallSoundInterval.finish()
        self.fallSoundInterval = None
        shrinkTrack = Sequence()
        if self.avatar.doId == base.localAvatar.doId:
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ == "DistributedSuit":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() > 0:
                            self.avatar.sendUpdate('suitHitByPie', [obj.doId, self.getID()])
                            hitCog = True
        if hitCog:
            SoundInterval(self.hitSfx, node = self.gag).start()
            shrinkTrack.append(Wait(0.5))
        else:
            SoundInterval(self.missSfx, node = self.gag).start()
        shrinkTrack.append(LerpScaleInterval(self.gag, 0.3, Point3(0.01, 0.01, 0.01), startScale = self.gag.getScale()))
        shrinkTrack.append(Func(self.cleanupGag))
        shrinkTrack.start()

    @abc.abstractmethod
    def startDrop(self):
        pass

    def cleanupLocationSeeker(self):
        if self.locationSeeker:
            self.dropLoc = self.locationSeeker.getLocation()
            self.locationSeeker.cleanup()
            self.locationSeeker = None

    def cleanupGag(self):
        if not self.isDropping:
            super(DropGag, self).cleanupGag()

    def release(self):
        self.build()
        self.cleanupLocationSeeker()
        self.isDropping = True
        Sequence(ActorInterval(self.avatar, self.buttonAnim, startFrame = self.chooseLocFrame,
                               endFrame = self.completeFrame, playRate = self.playRate), Func(self.startDrop)).start()
        self.fallSoundInterval = SoundInterval(self.fallSfx, node = self.avatar)
        Sequence(Wait(0.6), SoundInterval(self.buttonSfx, node = self.avatar), self.fallSoundInterval).start()

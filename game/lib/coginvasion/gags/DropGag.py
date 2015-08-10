"""

  Filename: DropGag.py
  Created by: DecodedLogic (16Jul15)

"""

from lib.coginvasion.gags.Gag import Gag
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.gags.GagState import GagState
from lib.coginvasion.globals import CIGlobals
from LocationGag import LocationGag
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Func, SoundInterval, Wait, LerpScaleInterval
from panda3d.core import CollisionNode, CollisionHandlerEvent, CollisionHandlerFloor, CollisionSphere, BitMask32, Point3
import abc

class DropGag(Gag, LocationGag):
    notify = directNotify.newCategory('DropGag')

    def __init__(self, name, model, anim, damage, hitSfx, missSfx, scale, playRate):
        Gag.__init__(self, name, model, damage, GagType.DROP, hitSfx, anim = anim, playRate = playRate, scale = scale, autoRelease = True)
        LocationGag.__init__(self, 10, 50)
        self.missSfx = None
        self.fallSoundPath = 'phase_5/audio/sfx/incoming_whistleALT.mp3'
        self.fallSoundInterval = None
        self.fallSfx = None
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.collHandlerF = CollisionHandlerFloor()
        self.fallDuration = 0.75
        self.isDropping = False
        if game.process == 'client':
            self.missSfx = base.audio3d.loadSfx(missSfx)
            self.fallSfx = base.audio3d.loadSfx(self.fallSoundPath)

    def completeDrop(self):
        LocationGag.complete(self)
        self.isDropping = False
        if game.process != 'client': return
        self.reset()
        if self.isLocal():
            base.localAvatar.enablePieKeys()

    def start(self):
        super(DropGag, self).start()
        LocationGag.start(self, self.avatar)

    def unEquip(self):
        LocationGag.cleanupLocationSeeker(self)
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

    def cleanupGag(self):
        if not self.isDropping:
            super(DropGag, self).cleanupGag()

    def release(self):
        LocationGag.release(self)
        self.build()
        self.isDropping = True
        self.fallSoundInterval = SoundInterval(self.fallSfx, node = self.avatar)
        actorTrack = LocationGag.getActorTrack(self)
        soundTrack = LocationGag.getSoundTrack(self)
        if actorTrack:
            actorTrack.append(Func(self.startDrop))
            actorTrack.start()
            soundTrack.append(self.fallSoundInterval)
            soundTrack.start()

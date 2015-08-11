"""

  Filename: DistributedPieTurret.py
  Created by: blach (14Jun15)
  Updated by: DecodedLogic (10Aug15)

"""

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from lib.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.battle.TurretGag import TurretGag
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpScaleInterval, LerpPosInterval, LerpColorScaleInterval, LerpQuatInterval, Func, Wait
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.distributed.ClockDelta import globalClockDelta
from panda3d.core import Point3, Vec3, Vec4, CollisionSphere, CollisionNode
import random

class DistributedPieTurret(DistributedAvatar, DistributedSmoothNode):
    notify = directNotify.newCategory('DistributedPieTurret')
    
    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)
        self.fsm = ClassicFSM(
            'DistributedPieTurret',
            [
                State('off', self.enterOff, self.exitOff),
                State('scan', self.enterScan, self.exitScan),
                State('shoot', self.enterShoot, self.exitShoot)
             ],
             'off', 'off'
         )
        self.fsm.enterInitialState()
        self.reloadTime = 0.25
        self.cannon = None
        self.track = None
        self.owner = None
        self.gag = None
        self.readyGag = None
        self.hitGag = None
        self.explosion = None
        self.wallCollNode = None
        self.eventCollNode = None
        self.event = None
        self.suit = None
        self.eventId = None
        self.entities = []
        
    def setOwner(self, avatar):
        self.owner = avatar
        
    def getOwner(self):
        return self.owner
        
    def setGag(self, name):
        self.gag = name
        if not self.readyGag:
            self.loadGagInTurret()
        
    def getGag(self):
        return self.gag
        
    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)
        
    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        DistributedSmoothNode.announceGenerate(self)
        self.healthLabel.setScale(1.1)
        self.makeTurret()
        
    def disable(self):
        self.fsm.requestFinalState()
        del self.fsm
        for ent in self.entities:
            ent.cleanup()
        self.entities = None
        if self.explosion:
            self.explosion.removeNode()
            self.explosion = None
        self.removeTurret()
        DistributedSmoothNode.disable(self)
        DistributedAvatar.disable(self)
        
    def showAndMoveHealthLabel(self):
        self.unstashHpLabel()
        self.stopMovingHealthLabel()
        moveTrack = LerpPosInterval(self.healthLabel,
                                duration = 0.5,
                                pos = Point3(0, 0, 5),
                                startPos = Point3(0, 0, 0),
                                blendType = 'easeOut')
        self.healthLabelTrack = Sequence(moveTrack, Wait(1.0), Func(self.stashHpLabel))
        self.healthLabelTrack.start()
        
    """ BEGIN STATES """
    
    def enterShoot(self, suitId):
        if self.cannon:
            smoke = loader.loadModel("phase_4/models/props/test_clouds.bam")
            smoke.setBillboardPointEye()
            smoke.reparentTo(self.cannon.find('**/cannon'))
            smoke.setPos(0, 6, -3)
            smoke.setScale(0.5)
            smoke.wrtReparentTo(render)
            self.suit = self.cr.doId2do.get(suitId)
            self.cannon.find('**/cannon').lookAt(self.suit.find('**/joint_head'))
            self.cannon.find('**/square_drop_shadow').headsUp(self.suit.find('**/joint_head'))
            track = Sequence(Parallel(LerpScaleInterval(smoke, 0.5, 3), LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.removeNode))
            track.start()
            self.createAndShootGag()
            
    def exitShoot(self):
        del self.suit
        
    def shoot(self, suitId):
        self.fsm.request('shoot', [suitId])
        
    def scan(self, timestamp = None, afterShooting = 0):
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        self.fsm.request('scan', [ts, afterShooting])
        
    def enterScan(self, ts = 0, afterShooting = 0):
        if afterShooting:
            self.track = Parallel(
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
                    startHpr = self.cannon.find('**/cannon').getHpr(), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
                    startHpr = self.cannon.find('**/square_drop_shadow').getHpr(), blendType = 'easeInOut'),
                name = "afterShootTrack" + str(id(self))
            )
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getDoneEvent(), self._afterShootTrackDone)
            self.track.start(ts)
        else:
            self.track = Parallel(
                Sequence(
                    LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (60, 0, 0),
                        startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                    LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
                        startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
                ),
                Sequence(
                    LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (60, 0, 0),
                        startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                    LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
                        startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
                )
            )
            self.track.loop(ts)
            
    def exitScan(self):
        if self.track:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            self.track = None
    
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
    
    """ END STATES """
    
    def _afterShootTrackDone(self):
        self.track = None
        self.track = Parallel(
            Sequence(
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (60, 0, 0),
                    startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/cannon'), duration = 3, quat = (-60, 0, 0),
                    startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
            ),
            Sequence(
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (60, 0, 0),
                    startHpr = Vec3(-60, 0, 0), blendType = 'easeInOut'),
                LerpQuatInterval(self.cannon.find('**/square_drop_shadow'), duration = 3, quat = (-60, 0, 0),
                    startHpr = Vec3(60, 0, 0), blendType = 'easeInOut'),
            )
        )
        self.track.loop()
    
    def makeTurret(self):
        self.cannon = loader.loadModel('phase_4/models/minigames/toon_cannon.bam')
        self.cannon.reparentTo(self)
        self.loadGagInTurret()
        self.setupWallSphere()
        if self.isLocal():
            self.setupEventSphere()
            
    def removeTurret(self):
        self.removeWallSphere()
        self.removeGagInTurret()
        if self.cannon:
            self.cannon.removeNode()
            self.cannon = None
            
    def getCannon(self):
        return self.cannon.find('**/cannon')
            
    def setupWallSphere(self):
        sphere = CollisionSphere(0.0, 0.0, 0.0, 3.0)
        node = CollisionNode('DistributedPieTurret.WallSphere')
        node.addSolid(sphere)
        node.setCollideMask(CIGlobals.WallBitmask)
        self.wallCollNode = self.cannon.attachNewNode(node)
        self.wallCollNode.setZ(2)
        self.wallCollNode.setY(1.0)
        
    def removeWallSphere(self):
        if self.wallCollNode:
            self.wallCollNode.removeNode()
            self.wallCollNode = None
            
    def createAndShootGag(self):
        if not self.readyGag:
            self.loadGagInTurret()
        self.readyGag.shoot(Point3(0, 200, -90))
        self.entities.append(self.readyGag)
        collideEventName = self.readyGag.getCollideEventName()
        self.readyGag = None
        if self.isLocal():
            self.acceptOnce(collideEventName, self.handleGagCollision)
        Sequence(Wait(self.reloadTime), Func(self.loadGagInTurret)).start()
        
    def loadGagInTurret(self):
        if self.cannon and self.gag:
            if self.readyGag:
                self.readyGag.cleanup()
                self.readyGag = None
            self.eventId = random.uniform(0, 100000000)
            self.readyGag = TurretGag(self, self.uniqueName('pieTurretCollision') + str(self.eventId), self.gag)
            self.readyGag.build()
            
    def makeSplat(self, pos):
        gagClass = self.hitGag.gagClass
        splat = gagClass.buildSplat(gagClass.splatScale, gagClass.splatColor)
        base.audio3d.attachSoundToObject(gagClass.hitSfx, splat)
        splat.reparentTo(render)
        splat.setPos(pos[0], pos[1], pos[2])
        gagClass.hitSfx.play()
        Sequence(Wait(0.5), Func(splat.cleanup)).start()
        self.hitGag = None
            
    def d_makeSplat(self, pos):
        self.sendUpdate('makeSplat', [pos])
        
    def b_makeSplat(self, pos):
        self.d_makeSplat(pos)
        self.makeSplat(pos)
            
    def handleGagCollision(self, entry, ent):
        x, y, z = ent.getGag().getPos(render)
        self.hitGag = ent
        self.b_makeSplat([x, y, z])
        if self.isLocal():
            intoNP = entry.getIntoNodePath()
            avNP = intoNP.getParent()
            for key in self.cr.doId2do.keys():
                obj = self.cr.doId2do[key]
                if obj.__class__.__name__ == 'DistributedSuit':
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() > 0:
                            base.localAvatar.sendUpdate('suitHitByPie', [obj.doId, ent.getID()])
        ent.cleanup()
        
    def setHealth(self, hp):
        DistributedAvatar.setHealth(self, hp)
        if self.isLocal():
            base.localAvatar.getMyBattle().getTurretManager().updateTurretGui()
            
    def die(self):
        self.fsm.requestFinalState()
        turretPos = self.cannon.getPos(render)
        self.removeTurret()
        self.explosion = loader.loadModel("phase_3.5/models/props/explosion.bam")
        self.explosion.setScale(0.5)
        self.explosion.reparentTo(render)
        self.explosion.setBillboardPointEye()
        self.explosion.setPos(turretPos + (0, 0, 1))
        sfx = base.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.mp3")
        base.audio3d.attachSoundToObject(sfx, self)
        base.playSfx(sfx)
        
    def isLocal(self):
        return self.getOwner() == base.localAvatar.doId
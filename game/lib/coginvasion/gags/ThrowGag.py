"""

  Filename: ThrowGag.py
  Created by: DecodedLogic (07Jul15)

"""

from panda3d.core import CollisionSphere, BitMask32, CollisionNode, NodePath, CollisionHandlerEvent
from direct.interval.ProjectileInterval import ProjectileInterval

from lib.coginvasion.gags.Gag import Gag
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.globals import CIGlobals
import GagGlobals

class ThrowGag(Gag):

    def __init__(self, name, model, damage, hitSfx, splatColor, anim = None, scale = 1):
        Gag.__init__(self, name, model, damage, GagType.THROW, hitSfx, anim = anim, scale = scale)
        self.splatScale = GagGlobals.splatSizes[self.name]
        self.splatColor = splatColor

    def start(self):
        super(ThrowGag, self).start()
        self.build()
        self.equip()
        self.avatar.setPlayRate(self.playRate, 'pie')
        self.avatar.play('pie', fromFrame = 0, toFrame = 45)
        if self.anim and self.gag: self.gag.play('chan')

    def throw(self):
        self.avatar.play('pie', fromFrame = 45, toFrame = 90)
        if not self.gag:
            self.build()
        if not self.handJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')
        self.gag.reparentTo(self.handJoint)

    def release(self):
        if self.gag == None: return
        super(ThrowGag, self).release()
        base.audio3d.attachSoundToObject(self.woosh, self.gag)
        self.woosh.play()

        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.avatar)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, 160, -90)
        throwPath.setHpr(90, -90, 90)

        self.gag.setScale(self.gag.getScale(render))
        self.gag.reparentTo(render)
        self.gag.setHpr(throwPath.getHpr(render))

        if not self.handJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')
        self.track = ProjectileInterval(self.gag, startPos = self.handJoint.getPos(render), endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        self.track.start()
        self.buildCollisions()
        self.reset()

    def handleSplat(self):
        if self.woosh: self.woosh.stop()
        self.buildSplat(self.splatScale, self.splatColor)
        base.audio3d.attachSoundToObject(self.hitSfx, self.splat)
        self.splat.reparentTo(render)
        self.splat.setPos(self.splatPos)
        self.hitSfx.play()
        self.cleanupGag()
        self.splatPos = None
        taskMgr.doMethodLater(0.5, self.delSplat, 'Delete Splat')
        return

    def onCollision(self, entry):
        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        if self.avatar.doId == base.localAvatar.doId:
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ == "DistributedSuit":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() > 0:
                            self.avatar.sendUpdate('suitHitByPie', [obj.doId, self.getID()])
                elif obj.__class__.__name__ == "DistributedToon":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() < obj.getMaxHealth() and not obj.isDead():
                            self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])
        if base.localAvatar == self.avatar:
            self.splatPos = self.gag.getPos(render)
            gagPos = self.gag.getPos(render)
            self.handleSplat()
            self.avatar.sendUpdate('setSplatPos', [self.getID(), gagPos.getX(), gagPos.getY(), gagPos.getZ()])

    def buildCollisions(self):
        pieSphere = CollisionSphere(0, 0, 0, 1)
        pieSensor = CollisionNode('gagSensor')
        pieSensor.addSolid(pieSphere)
        pieNP = self.gag.attach_new_node(pieSensor)
        pieNP.set_collide_mask(BitMask32(0))
        pieNP.node().set_from_collide_mask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)

        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.add_collider(pieNP, event)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

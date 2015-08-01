"""

  Filename: TrapGag.py
  Created by: DecodedLogic (08Jul15)

"""

from lib.coginvasion.gags.Gag import Gag
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.globals import CIGlobals
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.ProjectileInterval import ProjectileInterval
from panda3d.core import NodePath, CollisionSphere, CollisionNode, CollisionHandlerEvent, BitMask32
import abc

class TrapGag(Gag):

    def __init__(self, name, model, damage, idleSfx, hitSfx, particleFx, anim = None, wantParticles = True, autoRelease = False):
        Gag.__init__(self, name, model, damage, GagType.TRAP, hitSfx, anim = anim, autoRelease = autoRelease)
        self.audio3d = self.getAudio3D()
        self.particleFx = particleFx
        self.particles = None
        self.wantParticles = wantParticles
        self.idleSfx = None
        self.hitSfx = None
        self.entity = None
        if game.process == 'client':
            self.idleSfx = self.audio3d.loadSfx(idleSfx)
            self.hitSfx = self.audio3d.loadSfx(hitSfx)

    def build(self):
        super(TrapGag, self).build()
        self.buildParticles()

    @abc.abstractmethod
    def buildCollisions(self):
        if not self.gag: return
        gagSph = CollisionSphere(0, 0, 0, 1)
        gagSph.setTangible(0)
        gagNode = CollisionNode('gagSensor')
        gagNode.addSolid(gagSph)
        gagNP = self.gag.attach_new_node(gagNode)
        gagNP.setScale(0.75, 0.8, 0.75)
        gagNP.setPos(0.0, 0.1, 0.5)
        gagNP.setCollideMask(BitMask32.bit(0))
        gagNP.node().set_from_collide_mask(CIGlobals.FloorBitmask)

        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.addCollider(gagNP, event)

    @abc.abstractmethod
    def activate(self):
        pass

    @abc.abstractmethod
    def onCollision(self, entry):
        pass

    @abc.abstractmethod
    def d_doCollision(self):
        pass

    def delete(self):
        super(TrapGag, self).delete()
        self.cleanupParticles()

    def unEquip(self):
        super(TrapGag, self).unEquip()
        if self.gag:
            self.cleanupGag()
            if self.particles:
                self.cleanupParticles()

    @abc.abstractmethod
    def startTrap(self):
        super(TrapGag, self).start()
        if not self.handJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')
        if not self.gag:
            self.build()
        self.gag.reparentTo(self.handJoint)
        self.avatar.play('toss', fromFrame = 22)

    def throw(self):
        pass

    def release(self):
        super(TrapGag, self).release()
        if self.gag == None: return

        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.avatar)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, 160, -120)
        throwPath.setHpr(0, 90, 0)

        self.gag.setScale(self.gag.getScale(render))
        self.gag.reparentTo(render)
        self.gag.setHpr(throwPath.getHpr(render))

        self.track = ProjectileInterval(self.gag, startPos = self.handJoint.getPos(render), endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        self.track.start()
        self.buildCollisions()
        self.reset()
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def buildParticles(self):
        self.cleanupParticles()
        self.particles = ParticleEffect()
        self.particles.loadConfig(self.particleFx)

    def cleanupParticles(self):
        if self.particles:
            self.particles.cleanup()
            self.particles = None

    def getHandle(self):
        return self

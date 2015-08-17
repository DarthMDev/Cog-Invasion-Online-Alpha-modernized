"""

  Filename: TossTrapGag.py
  Created by: DecodedLogic (24Jul15)

"""

from lib.coginvasion.gags.TrapGag import TrapGag
from lib.coginvasion.globals import CIGlobals
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.IntervalGlobal import ProjectileInterval
from panda3d.core import NodePath, BitMask32, CollisionSphere, CollisionNode, CollisionHandlerEvent

class TossTrapGag(TrapGag):

    def __init__(self, name, model, damage, hitSfx, idleSfx = None, particlesFx = None, anim = None, wantParticles = True):
        TrapGag.__init__(self, name, model, damage, hitSfx, anim)
        self.wantParticles = wantParticles
        self.particles = None
        self.particlesFx = particlesFx
        self.idleSfx = None

        if game.process == 'client':
            if idleSfx:
                self.idleSfx = base.audio3d.loadSfx(idleSfx)

    def startTrap(self):
        TrapGag.startTrap(self)
        if not self.gag:
            self.build()
            self.setHandJoint()
        self.gag.reparentTo(self.handJoint)
        self.avatar.play('toss', fromFrame = 22)

    def build(self):
        TrapGag.build(self)
        self.buildParticles()
        self.setHandJoint()

    def buildParticles(self):
        self.cleanupParticles()
        if hasattr(self, 'wantParticles') and hasattr(self, 'particlesFx'):
            if self.wantParticles and self.particlesFx:
                self.particles = ParticleEffect()
                self.particles.loadConfig(self.particlesFx)

    def buildCollisions(self):
        TrapGag.buildCollisions(self)
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

    def onCollision(self, entry):
        TrapGag.onCollision(self, entry)
        gag = self.gag
        if not gag:
            gag = self.entity
        x, y, z = gag.getPos(render)
        self.avatar.sendUpdate('setGagPos', [self.getID(), x, y, z])

    def release(self):
        TrapGag.release(self)
        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.avatar)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, 160, -120)
        throwPath.setHpr(0, 90, 0)

        self.gag.setScale(self.gag.getScale(render))
        self.gag.wrtReparentTo(render)
        self.gag.setHpr(throwPath.getHpr(render))

        self.setHandJoint()
        self.track = ProjectileInterval(self.gag, startPos = self.handJoint.getPos(render), endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        self.track.start()
        self.buildCollisions()
        self.reset()
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def delete(self):
        TrapGag.delete(self)
        self.cleanupParticles()

    def unEquip(self):
        TrapGag.unEquip(self)
        self.cleanupParticles()

    def cleanupParticles(self):
        if self.particles:
            self.particles.cleanup()
            self.particles = None

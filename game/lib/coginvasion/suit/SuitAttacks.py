"""

  Filename: SuitAttacks.py
  Created by: blach (04Apr15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval, SoundInterval
from direct.interval.IntervalGlobal import ActorInterval, Parallel, LerpScaleInterval
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.showbase.DirectObject import DirectObject
from direct.distributed import DelayDelete
from panda3d.core import CollisionSphere, CollisionNode, CollisionHandlerEvent, NodePath, Vec3, VBase4, Point3, BitMask32
from lib.coginvasion.toon import ParticleLoader
from direct.actor.Actor import Actor
from lib.coginvasion.globals import CIGlobals
from direct.showutil.Rope import Rope
from direct.task import Task

class Attack(DirectObject):
    notify = directNotify.newCategory("Attack")

    def __init__(self, attacksClass, suit):
        self.attacksClass = attacksClass
        self.suit = suit
        self.attack = 'attack'
        self.suitTrack = None
        self.attackName2attackId = {}
        for index in range(len(CIGlobals.SuitAttacks)):
            self.attackName2attackId[CIGlobals.SuitAttacks[index]] = index

    def getAttackId(self, attackStr):
        return self.attackName2attackId[attackStr]

    def finishedAttack(self):
        messenger.send(self.attacksClass.doneEvent)

    def interruptAttack(self):
        self.cleanup()

    def cleanup(self):
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        self.attack = None
        self.suit = None
        self.attacksClass = None
        self.attackName2attackId = None

class ThrowAttack(Attack):
    notify = directNotify.newCategory("ThrowAttack")

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.attack = 'throw'
        self.weapon_state = None
        self.weapon = None
        self.wss = None
        self.wsnp = None
        self.suitTrack = None
        self.weaponSfx = None
        self.throwTrajectory = None

    def handleWeaponCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)
            self.suit.b_handleWeaponTouch()

    def doAttack(self, ts = 0):
        self.weapon_state = 'start'

    def playWeaponSound(self):
        if self.weapon and self.weaponSfx:
            self.suit.audio3d.attachSoundToObject(self.weaponSfx, self.suit)
            self.weaponSfx.play()

    def throwObject(self):
        self.acceptOnce("enter" + self.wsnp.node().getName(), self.handleWeaponCollision)
        self.playWeaponSound()
        if self.weapon:
            self.weapon.setScale(self.weapon.getScale(render))
            self.weapon.reparentTo(render)
            self.weapon.setHpr(Vec3(0, 0, 0))

    def interruptAttack(self):
        if self.throwTrajectory:
            if self.throwTrajectory.isStopped():
                self.delWeapon()

    def handleWeaponTouch(self):
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delWeapon()

    def delWeapon(self):
        if self.weapon:
            self.weapon.removeNode()
            self.weapon = None

    def cleanup(self):
        Attack.cleanup(self)
        self.weapon_state = None
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None
        self.delWeapon()
        self.wss = None
        if self.wsnp:
            self.wsnp.node().clearSolids()
            self.wsnp.removeNode()
            self.wsnp = None

class CannedAttack(ThrowAttack):
    notify = directNotify.newCategory("CannedAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'canned'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/can.bam")
        self.weapon.setScale(15)
        self.weapon.setR(180)
        self.wss = CollisionSphere(0,0,0,0.05)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doCannedAttack")
        else:
            name = "doCannedAttack"
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        self.suitTrack.append(Wait(1.2))
        self.suitTrack.append(Func(self.suit.setPlayRate, 1.0, 'throw-object'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(0))
        else:
            self.suitTrack.append(Wait(0.7))
        self.suit.setPlayRate(2.0, 'throw-object')
        self.suit.play('throw-object')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('cannedWeaponSphere')
        else:
            weaponCollId = 'cannedWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.mp3")
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        if not self.weapon:
            return
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = self.suit.find('**/joint_Rhold').getPos(render),
            endPos = pathNP.getPos(render),
            gravityMult = 0.7,
            duration = 1.0
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class HardballAttack(ThrowAttack):
    notify = directNotify.newCategory("HardballAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'playhardball'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/baseball.bam")
        self.weapon.setScale(10)
        self.wss = CollisionSphere(0,0,0,0.1)
        self.weapon.setZ(-0.5)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doHardballAttack")
        else:
            name = "doHardballAttack"
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        self.suitTrack.append(Wait(1.2))
        self.suitTrack.append(Func(self.suit.setPlayRate, 1.0, 'throw-object'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(0))
        else:
            self.suitTrack.append(Wait(0.7))
        self.suit.setPlayRate(2.0, 'throw-object')
        self.suit.play('throw-object')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('hardballWeaponSphere')
        else:
            weaponCollId = 'hardballWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_hardball_throw_only.mp3")
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        if not self.weapon:
            return
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = self.suit.find('**/joint_Rhold').getPos(render),
            endPos = pathNP.getPos(render),
            gravityMult = 0.7,
            duration = 1.0
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

    def handleWeaponTouch(self):
        if self.weaponSfx:
            self.weaponSfx.stop()
            self.weaponSfx = None
        ThrowAttack.handleWeaponTouch(self)

class ClipOnTieAttack(ThrowAttack):
    notify = directNotify.newCategory("ClipOnTieAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'clipontie'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/power-tie.bam")
        self.weapon.setScale(4)
        self.weapon.setR(180)
        self.wss = CollisionSphere(0,0,0,0.2)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doClipOnTieAttack")
        else:
            name = "doClipOnTieAttack"
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        self.suitTrack.append(Wait(1.2))
        self.suitTrack.append(Func(self.suit.setPlayRate, 1.0, 'throw-paper'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(0))
        else:
            self.suitTrack.append(Wait(0.7))
        self.suit.setPlayRate(2.0, 'throw-paper')
        self.suit.play('throw-paper')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('clipOnTieWeaponSphere')
        else:
            weaponCollId = 'clipOnTieWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.mp3")
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        if not self.weapon:
            return
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.weapon.setHpr(pathNP.getHpr(render))

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = self.suit.find('**/joint_Rhold').getPos(render),
            endPos = pathNP.getPos(render),
            gravityMult = 0.7,
            duration = 1.0
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

class MarketCrashAttack(ThrowAttack):
    notify = directNotify.newCategory("MarketCrashAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'marketcrash'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/newspaper.bam")
        self.weapon.setScale(3)
        self.weapon.setPos(0.41, -0.06, -0.06)
        self.weapon.setHpr(90, 0, 270)
        self.wss = CollisionSphere(0,0,0,0.35)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doMarketCrashAttack")
        else:
            name = "doMarketCrashAttack"
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        self.suitTrack.append(Wait(1.2))
        self.suitTrack.append(Func(self.suit.setPlayRate, 1.0, 'throw-paper'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(0))
        else:
            self.suitTrack.append(Wait(0.7))
        self.suit.setPlayRate(2.0, 'throw-paper')
        self.suit.play('throw-paper')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('marketCrashWeaponSphere')
        else:
            weaponCollId = 'marketCrashWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.wsnp.setPos(-0.25, 0.3, 0)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        if not self.weapon:
            return
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = self.suit.find('**/joint_Rhold').getPos(render),
            endPos = pathNP.getPos(render),
            gravityMult = 0.7,
            duration = 1.0
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

class SackedAttack(ThrowAttack):
    notify = directNotify.newCategory("SackedAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'sacked'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/sandbag-mod.bam")
        self.weapon.setScale(2)
        self.weapon.setR(180)
        self.weapon.setP(90)
        self.weapon.setY(-2.8)
        self.weapon.setZ(-0.3)
        self.wss = CollisionSphere(0,0,0,1)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doSackedAttack")
        else:
            name = "doSackedAttack"
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        self.suitTrack.append(Wait(1.2))
        self.suitTrack.append(Func(self.suit.setPlayRate, 1.0, 'throw-paper'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(0))
        else:
            self.suitTrack.append(Wait(0.7))
        self.suit.setPlayRate(2.0, 'throw-paper')
        self.suit.play('throw-paper')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('sackedWeaponSphere')
        else:
            weaponCollId = 'sackedWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.wsnp.setZ(1)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = None
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = self.suit.find('**/joint_Rhold').getPos(render),
            endPos = pathNP.getPos(render),
            gravityMult = 0.7,
            duration = 1.0
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

class GlowerPowerAttack(ThrowAttack):
    notify = directNotify.newCategory("GlowerPowerAttack")

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'glowerpower'

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.weapon = loader.loadModel("phase_5/models/props/dagger.bam")
        self.wss = CollisionSphere(0,0,0,1)
        self.wss.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName("doGlowerPowerAttack")
        else:
            name = "doGlowerPowerAttack"
        self.suitTrack = Sequence(name = name)
        self.suitTrack.append(Wait(1))
        self.suit.play("glower")
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.append(Wait(0.5))
        self.suitTrack.append(Func(self.delWeapon))
        if hasattr(self.suit, 'uniqueName'):
            weaponCollId = self.suit.uniqueName('glowerPowerWeaponSphere')
        else:
            weaponCollId = 'glowerPowerWeaponSphere'
        wsnode = CollisionNode(weaponCollId)
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def playWeaponSound(self):
        self.weaponSfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_glower_power.mp3")
        ThrowAttack.playWeaponSound(self)

    def throwObject(self):
        ThrowAttack.throwObject(self)
        pathNP = NodePath('throwPath')
        pathNP.reparentTo(self.suit)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 50, 0)
        pathNP.setHpr(0, 0, 0)

        self.weapon.setH(pathNP.getH(render))
        self.throwTrajectory = LerpPosInterval(
            self.weapon,
            duration = 0.5,
            pos = pathNP.getPos(render),
            startPos = (self.suit.getX(render), self.suit.getY(render) + 3, self.suit.find('**/joint_head').getZ(render))
        )
        self.throwTrajectory.start()
        self.weapon_state = 'released'

class PickPocketAttack(Attack):
    notify = directNotify.newCategory("PickPocketAttack")

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.attack = 'pickpocket'
        self.dollar = None
        self.pickSfx = None

    def doAttack(self, ts = 0):
        self.dollar = loader.loadModel("phase_5/models/props/1dollar-bill-mod.bam")
        self.dollar.setY(0.22)
        self.dollar.setHpr(289.18, 252.75, 0.00)
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doPickPocketAttack')
        else:
            name = 'doPickPocketAttack'
        self.suitTrack = Parallel(ActorInterval(self.suit, "pickpocket"),
            Sequence(Wait(0.4), Func(self.attemptDamage)), name = name)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def attemptDamage(self):
        shouldDamage = False
        suitH = self.suit.getH(render) % 360
        myH = base.localAvatar.getH(render) % 360
        if not -90.0 <= (suitH - myH) <= 90.0:
            if base.localAvatar.getDistance(self.suit) <= 15.0:
                shouldDamage = True
        if shouldDamage:
            self.playWeaponSound()
            self.dollar.reparentTo(self.suit.find('**/joint_Rhold'))
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)

    def playWeaponSound(self):
        self.pickSfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_pick_pocket.mp3")
        self.suit.audio3d.attachSoundToObject(self.pickSfx, self.suit)
        self.pickSfx.play()

    def cleanup(self):
        Attack.cleanup(self)
        if self.pickSfx:
            self.pickSfx.stop()
            self.pickSfx = None
        if self.dollar:
            self.dollar.removeNode()
            self.dollar = None

class FountainPenAttack(Attack):
    notify = directNotify.newCategory("FountainPenAttack")

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.attack = 'fountainpen'
        self.pen = None
        self.spray = None
        self.splat = None
        self.spraySfx = None
        self.sprayParticle = None
        self.sprayScaleIval = None
        self.wsnp = None

    def loadAttack(self):
        self.pen = loader.loadModel("phase_5/models/props/pen.bam")
        self.pen.reparentTo(self.suit.find('**/joint_Rhold'))
        self.sprayParticle = ParticleLoader.loadParticleEffect("phase_5/etc/penSpill.ptf")
        self.spray = loader.loadModel("phase_3.5/models/props/spray.bam")
        self.spray.setColor(VBase4(0, 0, 0, 1))
        self.splat = Actor("phase_3.5/models/props/splat-mod.bam",
            {"chan": "phase_3.5/models/props/splat-chan.bam"})
        self.splat.setColor(VBase4(0, 0, 0, 1))
        self.sprayScaleIval = LerpScaleInterval(
            self.spray,
            duration = 0.3,
            scale = (1, 20, 1),
            startScale = (1, 1, 1)
        )
        sphere = CollisionSphere(0, 0, 0, 0.5)
        sphere.setTangible(0)
        if hasattr(self.suit, 'uniqueName'):
            collName = self.suit.uniqueName('fountainPenCollNode')
        else:
            collName = 'fountainPenCollNode'
        collNode = CollisionNode(collName)
        collNode.addSolid(sphere)
        collNode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.spray.attachNewNode(collNode)
        self.wsnp.setY(1)
        #self.wsnp.show()

    def doAttack(self, ts = 0):
        self.loadAttack()
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doFountainPenAttack')
        else:
            name = 'doFountainPenAttack'
        self.suitTrack = Parallel(name = name)
        self.suitTrack.append(ActorInterval(self.suit, "fountainpen"))
        self.suitTrack.append(
            Sequence(
                Wait(1.2),
                Func(self.acceptOnce, "enter" + self.wsnp.node().getName(), self.handleSprayCollision),
                Func(self.playWeaponSound),
                Func(self.attachSpray),
                Func(self.sprayParticle.start, self.pen.find('**/joint_toSpray'), self.pen.find('**/joint_toSpray')),
                self.sprayScaleIval,
                Wait(0.5),
                Func(self.sprayParticle.cleanup),
                Func(self.spray.setScale, 1),
                Func(self.spray.reparentTo, hidden),
                Func(self.ignore, "enter" + self.wsnp.node().getName())
            )
        )
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def attachSpray(self):
        self.spray.reparentTo(self.pen.find('**/joint_toSpray'))
        #self.spray.setH(100)
        pos = self.spray.getPos(render)
        hpr = self.spray.getHpr(render)
        self.spray.reparentTo(render)
        self.spray.setPos(pos)
        self.spray.setHpr(hpr)
        self.spray.setP(0)
        if self.suit.type == "C":
            self.spray.setH(self.spray.getH() + 7.5)
        self.spray.setTwoSided(True)

    def handleSprayCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)
        self.sprayScaleIval.pause()

    def playWeaponSound(self):
        self.spraySfx = self.suit.audio3d.loadSfx("phase_5/audio/sfx/SA_fountain_pen.mp3")
        self.suit.audio3d.attachSoundToObject(self.spraySfx, self.pen)
        self.spraySfx.play()

    def cleanup(self):
        Attack.cleanup(self)
        if self.wsnp:
            self.wsnp.node().clearSolids()
            self.wsnp.removeNode()
            self.wsnp = None
        if self.pen:
            self.pen.removeNode()
            self.pen = None
        if self.sprayParticle:
            self.sprayParticle.cleanup()
            self.sprayParticle = None
        if self.spray:
            self.spray.removeNode()
            self.spray = None
        if self.splat:
            self.splat.cleanup()
            self.splat = None
        if self.sprayScaleIval:
            self.sprayScaleIval.pause()
            self.sprayScaleIval = None
        self.spraySfx = None

class HangUpAttack(Attack):
    notify = directNotify.newCategory("HangUpAttack")

    def __init__(self, attacksClass, suit):
        Attack.__init__(self, attacksClass, suit)
        self.attack = 'hangup'
        self.phone = None
        self.receiver = None
        self.collNP = None
        self.phoneSfx = None
        self.hangupSfx = None
        self.shootIval = None
        self.cord = None
        self.receiverOutCord = None
        self.phoneOutCord = None

    def loadAttack(self):
        self.phone = loader.loadModel("phase_3.5/models/props/phone.bam")
        self.phone.setHpr(0, 0, 180)
        if self.suit.type == "B":
            self.phone.setPos(0.7, 0.15, 0)
        elif self.suit.type == "C":
            self.phone.setPos(0.25, 0, 0)
        self.receiver = loader.loadModel("phase_3.5/models/props/receiver.bam")
        self.receiver.reparentTo(self.phone)
        self.cord = Rope()
        self.cord.ropeNode.setUseVertexColor(1)
        self.cord.ropeNode.setUseVertexThickness(1)
        self.cord.setup(3, ({'node': self.phone, 'point': (0.8, 0, 0.2), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': self.phone, 'point': (2, 0, 0), 'color': (0, 0, 0, 1), 'thickness': 1000}, {'node': self.receiver, 'point': (1.1, 0.25, 0.5), 'color': (0, 0, 0, 1), 'thickness': 1000}), [])
        self.cord.setH(180)
        self.phoneSfx = self.suit.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup.mp3")
        self.suit.audio3d.attachSoundToObject(self.phoneSfx, self.phone)
        self.hangupSfx = self.suit.audio3d.loadSfx("phase_3.5/audio/sfx/SA_hangup_place_down.mp3")
        self.suit.audio3d.attachSoundToObject(self.hangupSfx, self.phone)
        collSphere = CollisionSphere(0, 0, 0, 2)
        collSphere.setTangible(0)
        collNode = CollisionNode('phone_shootout')
        collNode.addSolid(collSphere)
        collNode.setCollideMask(CIGlobals.WallBitmask)
        self.collNP = self.phone.attachNewNode(collNode)
        #self.collNP.show()

    def doAttack(self, ts = 0):
        self.loadAttack()
        if hasattr(self.suit, 'uniqueName'):
            name = self.suit.uniqueName('doHangupAttack')
        else:
            name = 'doHangupAttack'
        if self.suit.type == "A":
            delay2playSound = 1.0
            delayAfterSoundToPlaceDownReceiver = 0.2
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.0
            receiverInHandPos = Point3(-0.5, 0.5, -1)
        elif self.suit.type == "B":
            delay2playSound = 1.5
            delayAfterSoundToPlaceDownReceiver = 0.7
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.5
            receiverInHandPos = Point3(-0.3, 0.5, -0.8)
        elif self.suit.type == "C":
            delay2playSound = 1.0
            delayAfterSoundToPlaceDownReceiver = 1.15
            delayAfterShootToIgnoreCollisions = 1.0
            delay2PickUpReceiver = 1.5
            receiverInHandPos = Point3(-0.3, 0.5, -0.8)
        self.suitTrack = Parallel(name = name)
        self.suitTrack.append(
            ActorInterval(self.suit, 'phone')
        )
        self.suitTrack.append(
            Sequence(
                Wait(delay2playSound),
                SoundInterval(self.phoneSfx, duration = 2.1),
                Wait(delayAfterSoundToPlaceDownReceiver),
                Func(self.receiver.setPos, 0, 0, 0),
                Func(self.receiver.setH, 0.0),
                Func(self.receiver.reparentTo, self.phone),
                Func(self.acceptOnce, "enter" + self.collNP.node().getName(), self.handleCollision),
                Func(self.shootOut),
                Parallel(
                    SoundInterval(self.hangupSfx),
                    Sequence(
                        Wait(delayAfterShootToIgnoreCollisions),
                        Func(self.ignore, "enter" + self.collNP.node().getName())
                    )
                )
            )
        )
        self.suitTrack.append(
            Sequence(
                Func(self.phone.reparentTo, self.suit.find('**/joint_Lhold')),
                Func(self.cord.reparentTo, render),
                Wait(delay2PickUpReceiver),
                Func(self.receiver.reparentTo, self.suit.find('**/joint_Rhold')),
                Func(self.receiver.setPos, receiverInHandPos),
                Func(self.receiver.setH, 270.0),
            )
        )
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.finishedAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self.suit, name)
        self.suitTrack.start(ts)

    def handleCollision(self, entry):
        if self.suit:
            self.suit.sendUpdate('toonHitByWeapon', [self.getAttackId(self.attack), base.localAvatar.doId])
            base.localAvatar.b_handleSuitAttack(self.getAttackId(self.attack), self.suit.doId)

    def shootOut(self):
        pathNode = NodePath('path')
        pathNode.reparentTo(self.suit)#.find('**/joint_Lhold'))
        pathNode.setPos(0, 50, self.phone.getZ(self.suit))

        self.collNP.reparentTo(render)

        self.shootIval = LerpPosInterval(
            self.collNP,
            duration = 1.0,
            pos = pathNode.getPos(render),
            startPos = self.phone.getPos(render)
        )
        self.shootIval.start()
        pathNode.removeNode()
        del pathNode

    def cleanup(self):
        Attack.cleanup(self)
        if self.shootIval:
            self.shootIval.pause()
            self.shootIval = None
        if self.cord:
            self.cord.removeNode()
            self.cord = None
        if self.phone:
            self.phone.removeNode()
            self.phone = None
        if self.receiver:
            self.receiver.removeNode()
            self.receiver = None
        if self.collNP:
            self.collNP.node().clearSolids()
            self.collNP.removeNode()
            self.collNP = None
        if self.phoneSfx:
            self.phoneSfx.stop()
            self.phoneSfx = None

class BounceCheckAttack(ThrowAttack):
    notify = directNotify.newCategory('BounceCheckAttack')
    MaxBounces = 3
    WeaponHitDistance = 0.5

    def __init__(self, attacksClass, suit):
        ThrowAttack.__init__(self, attacksClass, suit)
        self.attack = 'bouncecheck'
        self.bounceSound = None
        self.numBounces = 0

    def __pollCheckDistance(self, task):
        if base.localAvatar.getDistance(self.weapon) <= self.WeaponHitDistance:
            self.handleWeaponCollision(None)
            return Task.done
        else:
            return Task.cont

    def loadAttack(self):
        self.weapon = loader.loadModel('phase_5/models/props/bounced-check.bam')
        self.weapon.setScale(10)
        self.weapon.setTwoSided(1)
        self.bounceSound = self.suit.audio3d.loadSfx('phase_5/audio/sfx/SA_bounce_check_bounce.mp3')
        self.suit.audio3d.attachSoundToObject(self.bounceSound, self.suit)
        cSphere = CollisionSphere(0, 0, 0, 0.1)
        cSphere.setTangible(0)
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('bounced_check_collision')
        else:
            name = 'bounced_check_collision'
        cNode = CollisionNode(name)
        cNode.addSolid(cSphere)
        cNode.setFromCollideMask(CIGlobals.FloorBitmask)
        cNP = self.weapon.attachNewNode(cNode)
        cNP.setCollideMask(BitMask32(0))
        self.event = CollisionHandlerEvent()
        self.event.setInPattern('%fn-into')
        self.event.setOutPattern('%fn-out')
        base.cTrav.addCollider(cNP, self.event)
        self.wsnp = cNP
        self.wsnp.show()

    def doAttack(self, ts = 0):
        ThrowAttack.doAttack(self, ts)
        self.loadAttack()
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('doBounceCheckAttack')
        else:
            name = 'doBounceCheckAttack'
        self.suitTrack = Sequence(name = name)
        self.weapon.reparentTo(self.suit.find('**/joint_Rhold'))
        if self.suit.type == "C":
            self.suitTrack.append(Wait(2.3))
        else:
            self.suitTrack.append(Wait(3))
        self.suit.play('throw-paper')
        self.suitTrack.append(Func(self.throwObject))
        self.suitTrack.start(ts)

    def throwObject(self):
        ThrowAttack.throwObject(self)
        taskMgr.add(self.__pollCheckDistance, "pollCheckDistance")
        self.__doThrow(0)

    def __doThrow(self, alreadyThrown):
        self.weapon.setScale(1)
        pathNP = NodePath('throwPath')
        if not alreadyThrown:
            pathNP.reparentTo(self.suit)
        else:
            pathNP.reparentTo(self.weapon)
        pathNP.setScale(render, 1.0)
        pathNP.setPos(0, 30, -100)
        pathNP.setHpr(90, -90, 90)

        print pathNP.getPos(base.render)

        if self.throwTrajectory:
            self.throwTrajectory.pause()
            self.throwTrajectory = None

        if alreadyThrown:
            startPos = self.weapon.getPos(base.render)
            gravity = 0.7
        else:
            gravity = 0.7
            startPos = self.suit.find('**/joint_Rhold').getPos(base.render)

        self.throwTrajectory = ProjectileInterval(
            self.weapon,
            startPos = startPos,
            endPos = pathNP.getPos(base.render),
            gravityMult = gravity,
            duration = 3.0
        )
        self.throwTrajectory.start()
        self.weapon.setScale(10)
        self.weapon.reparentTo(render)
        self.weapon.setHpr(pathNP.getHpr(render))
        self.weapon_state = 'released'
        self.acceptOnce(self.wsnp.node().getName() + "-into", self.__handleHitFloor)

    def __handleHitFloor(self, entry):
        self.numBounces += 1
        # Bounce again if we still have bounces left.
        if self.numBounces >= self.MaxBounces:
            self.cleanup()
            return
        base.playSfx(self.bounceSound)
        self.__doThrow(1)

    def cleanup(self):
        taskMgr.remove("pollCheckDistance")
        self.ignore(self.wsnp.node().getName() + "-into")
        self.bounceSound = None
        ThrowAttack.cleanup(self)

from direct.fsm.StateData import StateData

class SuitAttacks(StateData):
    notify = directNotify.newCategory("SuitAttacks")
    attackName2attackClass = {
        "canned": CannedAttack,
        "playhardball": HardballAttack,
        "glowerpower": GlowerPowerAttack,
        "clipontie": ClipOnTieAttack,
        "marketcrash": MarketCrashAttack,
        "sacked": SackedAttack,
        "pickpocket": PickPocketAttack,
        "hangup": HangUpAttack,
        "fountainpen": FountainPenAttack,
        'bouncecheck': BounceCheckAttack,
    }

    def __init__(self, doneEvent, suit):
        StateData.__init__(self, doneEvent)
        self.suit = suit
        self.currentAttack = None

    def load(self, attackName):
        StateData.load(self)
        className = self.attackName2attackClass[attackName]
        self.currentAttack = className(self, self.suit)

    def enter(self, ts = 0):
        StateData.enter(self)
        self.currentAttack.doAttack(ts)

    def exit(self):
        self.currentAttack.cleanup()
        StateData.exit(self)

    def unload(self):
        self.cleanup()
        StateData.unload(self)

    def cleanup(self):
        self.suit = None
        self.currentAttack = None

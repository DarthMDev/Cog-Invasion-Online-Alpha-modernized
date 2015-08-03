"""

  Filename: ToonFPS.py
  Created by: blach (19Jan15)

"""

from pandac.PandaModules import *
from lib.coginvasion.globals import CIGlobals
from direct.actor.Actor import Actor
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.directnotify.DirectNotifyGlobal import directNotify
from ToonFPSGui import ToonFPSGui
from Bullet import Bullet
from direct.task import Task
from direct.distributed.ClockDelta import globalClockDelta
from direct.gui.DirectGui import *
import os
import random
from FirstPerson import FirstPerson

class ToonFPS(DirectObject):
    notify = directNotify.newCategory("ToonFPS")

    def __init__(self, mg, weaponName = "pistol"):
        self.mg = mg
        self.weaponName = weaponName
        self.v_model_root = None
        self.v_model = None
        self.weapon = None
        self.track = None
        self.draw = None
        self.shoot = None
        self.reload = None
        self.empty = None
        self.cockBack = None
        self.cockFwd = None
        self.player_node = None

        # blach (02Aug15)
        # Drastically improved the accuracy of bullets... DRASTICALLY
        self.shooterTrav = None
        self.shooterRay = None
        self.shooterRayNode = None
        self.shooterHandler = None

        self.gui = ToonFPSGui(self)
        self.fsm = ClassicFSM('ToonFPS', [State('off', self.enterOff, self.exitOff),
                State('alive', self.enterAlive, self.exitAlive),
                State('dead', self.enterDead, self.exitDead)],
                'off', 'off')
        #self.deadFSM = ClassicFSM('dead', [State('off', self.enterOff, self.exitOff),
        #		State('])
        self.aliveFSM = ClassicFSM('alive', [State('off', self.enterOff, self.exitOff),
                State('draw', self.enterDraw, self.exitDraw, ['idle']),
                State('idle', self.enterIdle, self.exitIdle, ['shoot', 'reload']),
                State('shoot', self.enterShoot, self.exitShoot, ['idle']),
                State('reload', self.enterReload, self.exitReload, ['idle'])],
                'off', 'off')
        self.fsm.getStateNamed('alive').addChild(self.aliveFSM)
        #self.fsm.getStateNamed('dead').addChild(self.deadFSM)
        self.fsm.enterInitialState()
        self.aliveFSM.enterInitialState()
        if self.weaponName == "pistol":
            self.ammo = 14
        elif self.weaponName == "shotgun":
            self.ammo = 7
        self.hp = 125
        self.max_hp = 125
        self.firstPerson = FirstPerson()

    def movementTask(self, task):
        if (
            not inputState.isSet('jump') and
            not base.localAvatar.walkControls.isAirborne and
            inputState.isSet('forward') or
            inputState.isSet('reverse') or
            inputState.isSet('slideLeft') or
            inputState.isSet('slideRight')
        ):
            if base.localAvatar.getAnimState() != "run":
                base.localAvatar.setAnimState('run')
                base.localAvatar.playMovementSfx("run")
                self.mg.sendUpdate("runningAvatar", [base.localAvatar.doId])
        elif (
            inputState.isSet('jump') or
            base.localAvatar.walkControls.isAirborne
        ):
            if base.localAvatar.getAnimState() != "jump":
                base.localAvatar.setAnimState("jump")
                base.localAvatar.playMovementSfx(None)
                self.mg.sendUpdate("jumpingAvatar", [base.localAvatar.doId])
        else:
            if base.localAvatar.getAnimState() != "neutral":
                base.localAvatar.setAnimState("neutral")
                base.localAvatar.playMovementSfx(None)
                self.mg.sendUpdate("standingAvatar", [base.localAvatar.doId])
        return Task.cont

    def enterAlive(self):
        base.localAvatar.disableChatInput()
        self.start()
        self.resetHp()
        self.resetAmmo()
        if self.mg.fsm.getCurrentState().getName() == "play":
            self.reallyStart()

    def exitAlive(self):
        self.end()
        self.v_model.reparentTo(hidden)
        if self.mg.fsm.getCurrentState().getName() != "play":
            self.reallyEnd()
        base.localAvatar.createChatInput()

    def updatePoints(self):
        self.points = self.kills - self.deaths

    def enterDead(self, killer):
        base.localAvatar.getGeomNode().show()
        self.gui.end()
        base.localAvatar.attachCamera()
        self.freezeCamSfx = base.loadSfx("phase_4/audio/sfx/freeze_cam.wav")
        self.freezeCamImage = None
        self.freezeCamImageFile = None
        base.camera.setZ(base.camera.getZ() + 2.0)
        taskMgr.add(
            self.cameraLookAtKillerTask,
            "lookAtKiller",
            extraArgs = [killer],
            appendTask = True
        )
        taskMgr.doMethodLater(
            2.0,
            self.startZoomOnKiller,
            "startFreezeCam",
            extraArgs = [killer],
            appendTask = True
        )

    def startZoomOnKiller(self, killer, task):
        taskMgr.add(
            self.__zoomOnKillerTask,
            "zoomOnKiller",
            extraArgs = [killer],
            appendTask = True
        )
        return task.done

    def __zoomOnKillerTask(self, killer, task):
        if base.camera.getDistance(killer) <= 10.0 and self.freezeCamSfx.status() == self.freezeCamSfx.READY:
            base.playSfx(self.freezeCamSfx)
        if base.camera.getDistance(killer) < 7.0:
            self.doFreezeCam()
            return task.done
        base.camera.setY(base.camera, 60 * globalClock.getDt())
        return task.again

    def doFreezeCam(self):
        taskMgr.remove("lookAtKiller")
        self.frameBuffer = PNMImage()
        base.win.getScreenshot(self.frameBuffer)
        self.freezeCamTex = Texture()
        self.freezeCamTex.load(self.frameBuffer)
        self.freezeCamImage = OnscreenImage(image = self.freezeCamTex, parent=render2d)

    def cameraLookAtKillerTask(self, killer, task):
        base.camera.lookAt(killer, 0, 0, 3)
        return task.cont

    def exitDead(self):
        taskMgr.remove("zoomOnKiller")
        taskMgr.remove("lookAtKiller")
        taskMgr.remove("startFreezeCam")
        del self.freezeCamSfx
        if self.freezeCamImage:
            self.freezeCamImage.destroy()
        del self.freezeCamImage
        self.frameBuffer.clear()
        self.freezeCamTex.clear()
        del self.frameBuffer
        del self.freezeCamTex
        base.localAvatar.detachCamera()
        base.localAvatar.getGeomNode().hide()
        self.gui.start()

    def load(self):
        if self.weaponName == "pistol":
            self.draw = base.loadSfx("phase_4/audio/sfx/draw_secondary.wav")
            self.shoot = base.loadSfx("phase_4/audio/sfx/pistol_shoot.wav")
            self.reload = base.loadSfx("phase_4/audio/sfx/pistol_worldreload.wav")
        elif self.weaponName == "shotgun":
            self.draw = base.loadSfx("phase_4/audio/sfx/draw_primary.wav")
            self.shoot = base.loadSfx("phase_4/audio/sfx/shotgun_shoot.wav")
            self.cockBack = base.loadSfx("phase_4/audio/sfx/shotgun_cock_back.wav")
            self.cockFwd = base.loadSfx("phase_4/audio/sfx/shotgun_cock_forward.wav")
        self.empty = base.loadSfx("phase_4/audio/sfx/shotgun_empty.wav")
        self.v_model_root = base.camera.attachNewNode('v_model_root')
        self.v_model = Actor('phase_4/models/minigames/v_dgm.egg', {'pidle': 'phase_4/models/minigames/v_dgm-pistol-idle.egg',
                    'pshoot': 'phase_4/models/minigames/v_dgm-pistol-shoot.egg',
                    'preload': 'phase_4/models/minigames/v_dgm-pistol-reload.egg',
                    'pdraw': 'phase_4/models/minigames/v_dgm-pistol-draw.egg',
                    'sidle': 'phase_4/models/minigames/v_dgm-shotgun-idle.egg',
                    'sshoot': 'phase_4/models/minigames/v_dgm-shotgun-shoot.egg'})
        if self.weaponName == "pistol":
            self.weapon = loader.loadModel("phase_4/models/props/water-gun.bam")
            self.weapon.reparentTo(self.v_model.exposeJoint(None, "modelRoot", "Bone.011"))
            self.weapon.setX(-0.125)
            self.weapon.setY(0.5)
            self.weapon.setScale(0.65)
        elif self.weaponName == "shotgun":
            self.weapon = loader.loadModel("phase_4/models/props/shotgun.egg")
            self.weapon.reparentTo(self.v_model.exposeJoint(None, "modelRoot", "Bone.029"))
            self.weapon.setScale(0.75)
            self.weapon.setPos(0.45, -1.03, -1.17)
            self.weapon.setHpr(9.46, 308.19, 75.78)
            color = random.choice(
                [
                    VBase4(1, 0.25, 0.25, 1),
                    VBase4(0.25, 1, 0.25, 1),
                    VBase4(0.25, 0.25, 1, 1)
                ]
            )
            self.weapon.setColorScale(color)
        self.gui.load()

    def start(self):
        base.camLens.setNear(0.1)

        self.shooterTrav = CollisionTraverser('ToonFPS.shooterTrav')
        ray = CollisionRay()
        rayNode = CollisionNode('ToonFPS.rayNode')
        rayNode.addSolid(ray)
        rayNode.setCollideMask(BitMask32(0))
        rayNode.setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)
        self.shooterRay = ray
        self.shooterRayNode = base.camera.attachNewNode(rayNode)
        self.shooterHandler = CollisionHandlerQueue()
        self.shooterTrav.addCollider(self.shooterRayNode, self.shooterHandler)

        self.firstPerson.start()
        self.v_model_root.reparentTo(base.camera)
        self.v_model.reparentTo(self.v_model_root)
        if self.weaponName == "pistol":
            self.v_model_root.setZ(-1.8)
            self.v_model_root.setY(0.3)
            self.v_model_root.setX(-0.1)
            self.v_model_root.setH(2)
        elif self.weaponName == "shotgun":
            self.v_model_root.setPos(-0.42, -0.81, -1.7)
            self.v_model_root.setHpr(359, 352.87, 0.00)
        self.gui.start()
        self.firstPerson.disableMouse()
        self.aliveFSM.request('draw')

    def reallyStart(self):
        self.firstPerson.reallyStart()
        taskMgr.add(self.movementTask, "toonBattleMovement")

    def end(self):
        self.aliveFSM.request('off')
        self.firstPerson.enableMouse()
        self.firstPerson.end()
        taskMgr.remove("toonBattleMovement")
        if self.mg.fsm.getCurrentState().getName() != "play":
            self.fsm.request('off')

    def reallyEnd(self):
        self.shooterRayNode.removeNode()
        self.shooterRayNode = None
        self.shooterRay = None
        self.shooterTrav = None
        self.shooterHandler = None
        self.firstPerson.reallyEnd()
        self.v_model_root.reparentTo(hidden)
        self.v_model.reparentTo(hidden)
        self.v_model.setPosHpr(0, 0, 0, 0, 0, 0)
        self.gui.end()
        base.camLens.setNear(1.0)

    def cleanup(self):
        taskMgr.remove("lookAtKiller")
        taskMgr.remove("toonBattleMovement")
        self.firstPerson.cleanup()
        self.firstPerson = None
        self.draw = None
        self.shoot = None
        self.reload = None
        self.empty = None
        self.ammo = None
        self.fsm = None
        self.aliveFSM = None
        self.player_node = None
        self.min_camerap = None
        self.max_camerap = None
        self.hp = None
        self.max_hp = None
        self.v_model.cleanup()
        self.v_model = None
        self.weapon.removeNode()
        self.weapon = None
        self.v_model_root.removeNode()
        self.v_model_root = None
        self.gui.cleanup()

    def damageTaken(self, amount, avId):
        if self.hp <= 0.0:
            killer = self.mg.cr.doId2do.get(avId, None)
            self.fsm.request('dead', [killer])
        self.gui.adjustHpMeter()

    def enterDraw(self):
        self.draw.play()
        if self.weaponName == "pistol":
            self.track = ActorInterval(self.v_model, 'pdraw', playRate = 1.6, name = 'drawTrack')
        elif self.weaponName == "shotgun":
            self.v_model.loop("sidle")
            self.track = LerpQuatInterval(self.v_model, duration = 0.5, quat = (0, 0, 0),
                startHpr = (70, -50, 0), blendType = 'easeOut', name = 'drawTrack')
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getDoneEvent(), self.aliveFSM.request, ['idle'])
        self.track.start()

    def exitDraw(self):
        #self.draw.stop()
        if self.track:
            self.ignore(self.track.getDoneEvent())
            self.track.finish()
            self.track = None

    def enterIdle(self):
        if self.weaponName == "pistol":
            self.v_model.loop('pidle')
        elif self.weaponName == "shotgun":
            self.v_model.loop('sidle')
        self.accept('mouse1', self.requestShoot)
        if self.ammo <= 0:
            self.gui.notifyNoAmmo()
        if self.ammo < 14:
            self.accept('r', self.aliveFSM.request, ['reload'])

    def requestShoot(self):
        if self.mg.fsm.getCurrentState().getName() != "play":
            return
        if self.ammo > 0:
            self.aliveFSM.request('shoot')
        else:
            self.empty.play()

    def exitIdle(self):
        self.v_model.stop()
        self.ignore('mouse1')
        self.ignore('r')

    def enterShoot(self):
        self.shoot.play()
        if self.weaponName == "pistol":
            self.track = ActorInterval(self.v_model, 'pshoot', playRate = 2, name = 'shootTrack')
        elif self.weaponName == "shotgun":
            self.track = Sequence(ActorInterval(self.v_model, 'sshoot', playRate = 1.5), Wait(0.1), name = 'shootTrack')
        self.track.setDoneEvent('shootTrack')
        self.acceptOnce(self.track.getDoneEvent(), self.aliveFSM.request, ['idle'])
        self.track.start()
        self.ammo -= 1
        self.gui.adjustAmmoGui()

    def exitShoot(self):
        #self.shoot.stop()
        self.ignore('shootTrack')
        if self.track:
            self.track.finish()
            self.track = None

    def enterReload(self):
        self.gui.deleteNoAmmoLabel()
        if self.weaponName == "pistol":
            self.track = Parallel(Sequence(Wait(0.3), Func(self.reload.play), Func(self.resetAmmo)),
                ActorInterval(self.v_model, 'preload', playRate = 1.5), name = 'reloadTrack')
        elif self.weaponName == "shotgun":
            self.track = Sequence(Func(self.draw.play), LerpQuatInterval(self.v_model, duration = 0.5,
                quat = (70, -50, 0), startHpr = (0, 0, 0), blendType = 'easeIn'),
                SoundInterval(self.cockBack),
                SoundInterval(self.cockFwd),
                Func(self.resetAmmo),
                Func(self.draw.play),
                LerpQuatInterval(self.v_model, duration = 0.5, quat = (0, 0, 0), startHpr = (70, -50, 0),
                    blendType = 'easeOut'), name = 'reloadTrack')
        self.track.setDoneEvent('reloadTrack')
        self.acceptOnce(self.track.getDoneEvent(), self.aliveFSM.request, ['idle'])
        self.track.start()

    def exitReload(self):
        #self.reload.stop()
        self.ignore('reloadTrack')
        if self.track:
            self.track.finish()
            self.track = None

    def resetAmmo(self):
        if self.weaponName == "pistol":
            self.ammo = 14
        elif self.weaponName == "shotgun":
            self.ammo = 7
        self.gui.resetAmmo()

    def resetHp(self):
        self.hp = self.max_hp
        self.gui.adjustHpMeter()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

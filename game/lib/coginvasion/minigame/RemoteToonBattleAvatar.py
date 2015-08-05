"""

  Filename: RemoteToonBattleAvatar.py
  Created by: blach (20Jan15)

"""

from panda3d.core import VBase4
from lib.coginvasion.globals import CIGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from Bullet import Bullet
from RemoteAvatar import RemoteAvatar

class RemoteToonBattleAvatar(RemoteAvatar):
    notify = directNotify.newCategory("RemoteToonBattleAvatar")

    def __init__(self, mg, cr, avId, gunName = "pistol"):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.track = None
        self.gunName = gunName
        self.fsm = ClassicFSM(
            'RemoteToonBattleAvatar',
            [
                State(
                    'off',
                    self.enterOff,
                    self.exitOff
                ),
                State(
                    'shoot',
                    self.enterShoot,
                    self.exitShoot
                ),
                State(
                    'die',
                    self.enterDie,
                    self.exitDie
                ),
                State(
                    'dead',
                    self.enterDead,
                    self.exitDead
                )
            ],
            'off',
            'off'
        )
        self.fsm.enterInitialState()
        self.soundGrunt = None
        self.retrieveAvatar()

    def setGunName(self, gunName):
        self.gunName = gunName
        self.avatar.attachGun(gunName)

    def getGunName(self):
        return self.gunName

    def retrieveAvatar(self):
        RemoteAvatar.retrieveAvatar(self)
        if self.avatar:
            self.avatar.attachGun(self.gunName)
            self.soundGrunt = self.avatar.audio3d.loadSfx('phase_4/audio/sfx/target_impact_grunt1.mp3')
            self.avatar.audio3d.attachSoundToObject(self.soundGrunt, self.avatar)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def grunt(self):
        base.playSfx(self.soundGrunt)

    def enterDead(self):
        if self.avatar:
            self.avatar.stash()

    def exitDead(self):
        if self.avatar:
            self.avatar.unstash()
            self.avatar.clearColorScale()
            self.avatar.getGeomNode().clearColorScale()
            self.avatar.clearTransparency()
            self.avatar.getGeomNode().clearTransparency()
            self.avatar.getNameTag().clearColorScale()

    def enterDie(self, ts):
        if self.avatar:
            dieSound = self.audio3d.loadSfx(self.avatar.getToonAnimalNoise('exclaim'))
            self.audio3d.attachSoundToObject(dieSound, self.avatar)
            self.avatar.setTransparency(1)
            self.avatar.getGeomNode().setTransparency(1)
            self.track = Sequence(
                Func(dieSound.play),
                Parallel(
                    LerpColorScaleInterval(
                        self.avatar.getGeomNode(),
                        colorScale = VBase4(1, 1, 1, 0),
                        startColorScale = VBase4(1, 1, 1, 1),
                        duration = 0.5
                    ),
                    LerpColorScaleInterval(
                        self.avatar.getNameTag(),
                        colorScale = VBase4(1, 1, 1, 0),
                        startColorScale = VBase4(1, 1, 1, 1),
                        duration = 0.5
                    ),
                    ActorInterval(
                        self.avatar,
                        'fallb'
                    )
                ),
                Func(self.fsm.request, 'dead')
            )
            self.track.start(ts)
            del dieSound

    def exitDie(self):
        self.resetTrack()

    def resetTrack(self):
        if self.track:
            self.track.pause()
            self.track = None
        #self.avatar.stop()

    def run(self):
        if self.avatar:
            if self.track and self.track.isPlaying():
                self.avatar.loop('run', partName = 'legs')
            else:
                self.avatar.loop('run')

    def stand(self):
        if self.avatar:
            if self.track and self.track.isPlaying():
                self.avatar.loop('neutral', partName = 'legs')
            else:
                self.avatar.loop('neutral')

    def jump(self):
        if self.avatar:
            if self.track and self.track.isPlaying():
                self.avatar.loop('jump', partName = 'legs')
            else:
                self.avatar.loop('jump')

    def enterShoot(self, ts):
        if self.avatar:

            def createBullet():
                if self.gunName == "pistol":
                    Bullet(self.mg, self.avatar.gun.find('**/joint_nozzle'), 0, self.gunName)
                elif self.gunName == "shotgun":
                    b1 = Bullet(self.mg, self.avatar.gun.find('**/joint_nozzle'), 0, self.gunName)
                    b2 = Bullet(self.mg, self.avatar.gun.find('**/joint_nozzle'), 0, self.gunName)

            def changeToLegAnim():
                self.avatar.loop(self.avatar.getCurrentAnim(partName = 'legs'))

            if self.gunName == "pistol":
                gunSound = self.audio3d.loadSfx("phase_4/audio/sfx/pistol_shoot.wav")
            elif self.gunName == "shotgun":
                gunSound = self.audio3d.loadSfx("phase_4/audio/sfx/shotgun_shoot.wav")
            self.audio3d.attachSoundToObject(gunSound, self.avatar)
            self.track = Sequence(
                Func(createBullet),
                Func(gunSound.play),
                ActorInterval(
                    self.avatar,
                    "squirt",
                    partName = 'torso',
                    startFrame = 48,
                    endFrame = 58
                ),
                ActorInterval(
                    self.avatar,
                    "squirt",
                    partName = 'torso',
                    startFrame = 107,
                    endFrame = 126,
                    playRate = 3
                ),
                Func(changeToLegAnim)
            )
            self.track.start(ts)
            del gunSound

            self.mg.makeSmokeEffect(self.avatar.gun.find('**/joint_nozzle').getPos(render))

    def exitShoot(self):
        self.resetTrack()

    def cleanup(self):
        if self.avatar:
            self.avatar.detachGun()
            if self.soundGrunt:
                self.avatar.audio3d.detachSound(self.soundGrunt)
                self.soundGrunt = None
        if self.track:
            self.track.pause()
        del self.track
        RemoteAvatar.cleanup(self)

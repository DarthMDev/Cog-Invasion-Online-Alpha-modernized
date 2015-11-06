"""

  Filename: DistributedGunGame.py
  Created by: blach (26Oct14)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.minigame.GunGameToonFPS import GunGameToonFPS
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
from DistributedToonFPSGame import DistributedToonFPSGame
import GunGameLevelLoader

import random

class DistributedGunGame(DistributedToonFPSGame):
    notify = directNotify.newCategory("DistributedGunGame")

    def __init__(self, cr):
        try:
            self.DistributedGunGame_initialized
            return
        except:
            self.DistributedGunGame_initialized = 1
        DistributedToonFPSGame.__init__(self, cr)
        self.fsm.addState(State('countdown', self.enterCountdown, self.exitCountdown, ['play']))
        self.fsm.addState(State('announceGameOver', self.enterAnnounceGameOver, self.exitAnnounceGameOver, ['finalScores']))
        self.fsm.addState(State('finalScores', self.enterFinalScores, self.exitFinalScores, ['gameOver']))
        self.fsm.addState(State('chooseGun', self.enterChooseGun, self.exitChooseGun, ['waitForOthers']))
        self.fsm.getStateNamed('start').addTransition('chooseGun')
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.fsm.getStateNamed('play').addTransition('announceGameOver')
        self.toonFps = GunGameToonFPS(self)
        self.loader = GunGameLevelLoader.GunGameLevelLoader()
        self.track = None
        self.isTimeUp = False
        self.cameraMovmentSeq = None
        self.gameMode = None
        return

    def setGameMode(self, mode):
        self.gameMode = mode

    def getGameMode(self):
        return self.gameMode

    def avatarHitByBullet(self, avId, damage):
        avatar = self.getRemoteAvatar(avId)
        if avatar:
            avatar.grunt()

    def headBackToMinigameArea(self):
        if self.loader:
            self.loader.unload()
            self.loader.cleanup()
            self.loader = None
        DistributedToonFPSGame.headBackToMinigameArea(self)

    def attachGunToAvatar(self, avId):
        self.remoteAvatars.append(RemoteToonBattleAvatar(self, self.cr, avId))

    def setLevelName(self, levelName):
        self.loader.setLevel(levelName)

    def pickSpawnPoint(self):
        return random.choice(self.loader.getSpawnPoints())

    def load(self):
        self.loader.load()
        pos, hpr = self.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)
        self.toonFps.load()
        self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
        self.setMinigameMusic("phase_4/audio/bgm/MG_TwoDGame.mid")
        self.setDescription("Battle and defeat the other Toons with your gun to gain points. " + \
                            "Remember to reload your gun when you're out of ammo! " + \
                            "The Toon with the most points when the timer runs out gets a nice prize!")
        self.setWinnerPrize(70)
        self.setLoserPrize(15)
        pos, hpr = self.loader.getCameraOfCurrentLevel()
        camera.setPos(pos)
        camera.setHpr(hpr)
        DistributedToonFPSGame.load(self)

    def enterChooseGun(self):
        font = CIGlobals.getToonFont()
        box = DGG.getDefaultDialogGeom()
        geom = CIGlobals.getDefaultBtnGeom()
        self.container = DirectFrame()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4),
            parent = self.container)
        self.title = OnscreenText(text = "Choose A Gun", pos = (0, 0.5, 0), font = font, scale = (0.12), parent = self.container)
        self.pistolBtn = DirectButton(geom = geom, text = "Pistol", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["pistol"], pos = (0, 0, 0.35), parent = self.container)
        self.shotgunBtn = DirectButton(geom = geom, text = "Shotgun", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["shotgun"], pos = (0, 0, 0.25), parent = self.container)

    def __gunChoice(self, choice):
        self.toonFps.cleanup()
        self.toonFps = None
        self.toonFps = GunGameToonFPS(self, choice)
        self.toonFps.load()
        self.d_ready()
        self.fsm.request('waitForOthers')

    def exitChooseGun(self):
        self.shotgunBtn.destroy()
        del self.shotgunBtn
        self.pistolBtn.destroy()
        del self.pistolBtn
        self.title.destroy()
        del self.title
        self.bg.destroy()
        del self.bg
        self.container.destroy()
        del self.container

    def gunChoice(self, choice, avId):
        remoteAvatar = self.getRemoteAvatar(avId)
        if remoteAvatar:
            remoteAvatar.setGunName(choice)

    def handleDescAck(self):
        self.fsm.request('chooseGun')

    def incrementKills(self):
        self.toonFps.killedSomebody()

    def allPlayersReady(self):
        self.fsm.request('countdown')

    def timeUp(self):
        if not self.isTimeUp:
            self.fsm.request('announceGameOver')
            self.isTimeUp = True

    def enterAnnounceGameOver(self):
        whistleSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.mp3")
        whistleSfx.play()
        del whistleSfx
        self.gameOverLbl = DirectLabel(text = "TIME'S\nUP!", relief = None, scale = 0.35, text_font = CIGlobals.getMickeyFont(), text_fg = (1, 0, 0, 1))
        self.track = Sequence(Wait(3.0), Func(self.fsm.request, 'finalScores'))
        self.track.start()

    def exitAnnounceGameOver(self):
        self.gameOverLbl.destroy()
        del self.gameOverLbl
        if self.track:
            self.track.pause()
            self.track = None

    def enterFinalScores(self):
        DistributedToonFPSGame.enterFinalScores(self)
        self.sendUpdate('myFinalScore', [self.toonFps.points])

    def enterCountdown(self):
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)
        self.toonFps.fsm.request('alive')
        text = OnscreenText(text = "", scale = 0.1, pos = (0, 0.5), fg = (1, 1, 1, 1), shadow = (0,0,0,1))
        self.track = Sequence(
            Func(text.setText, "5"),
            Wait(1.0),
            Func(text.setText, "4"),
            Wait(1.0),
            Func(text.setText, "3"),
            Wait(1.0),
            Func(text.setText, "2"),
            Wait(1.0),
            Func(text.setText, "1"),
            Wait(1.0),
            Func(text.setText, "FIGHT!"),
            Func(self.fsm.request, 'play'),
            Wait(1.0),
            Func(text.destroy)
        )
        self.track.start()
        self.sendUpdate('gunChoice', [self.toonFps.weaponName, base.localAvatar.doId])

    def exitCountdown(self):
        if self.track:
            self.track.finish()
            self.track = None

    def enterPlay(self):
        DistributedToonFPSGame.enterPlay(self)
        self.toonFps.reallyStart()
        self.createTimer()

    def exitPlay(self):
        self.deleteTimer()
        if self.toonFps:
            self.toonFps.end()
        base.localAvatar.createChatInput()
        DistributedToonFPSGame.exitPlay(self)

    def announceGenerate(self):
        DistributedToonFPSGame.announceGenerate(self)
        self.load()
        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))

    def disable(self):
        DistributedToonFPSGame.disable(self)
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        if self.loader:
            self.loader.unload()
            self.loader.cleanup()
            self.loader = None
        self.isTimeUp = None
        self.toonFps.reallyEnd()
        self.toonFps.cleanup()
        self.toonFps = None
        self.spawnPoints = None

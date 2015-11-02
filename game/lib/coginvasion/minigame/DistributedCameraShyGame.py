"""

  Filename: DistributedCameraShyGame.py
  Created by: blach (26Apr15)

"""

from panda3d.core import Point3, Vec3, CompassEffect, NodePath
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpScaleInterval
from direct.gui.DirectGui import OnscreenText
from direct.task import Task

import random

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.SkyUtil import SkyUtil
from DistributedMinigame import DistributedMinigame
from RemoteCameraShyAvatar import RemoteCameraShyAvatar
from CameraShyFirstPerson import CameraShyFirstPerson
from CameraShyHeadPanels import CameraShyHeadPanels

class DistributedCameraShyGame(DistributedMinigame):
    notify = directNotify.newCategory("DistributedCameraShyGame")

    def __init__(self, cr):
        try:
            self.DistributedCameraShyGame_initialized
            return
        except:
            self.DistributedCameraShyGame_initialized = 1
        DistributedMinigame.__init__(self, cr)
        self.headPanels.delete()
        self.headPanels = CameraShyHeadPanels()
        self.fsm.addState(State('countdown', self.enterCountdown, self.exitCountdown, ['play']))
        self.fsm.addState(State('announceGameOver', self.enterAnnounceGameOver, self.exitAnnounceGameOver, ['showWinner']))
        self.fsm.addState(State('showWinner', self.enterShowWinner, self.exitShowWinner, ['gameOver']))
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.fsm.getStateNamed('play').addTransition('announceGameOver')
        self.maze = None
        self.mazeCollModel = None
        self.spawnPoints = []
        self.remoteAvatars = []
        self.myRemoteAvatar = None
        self.thisPlayerWinsLbl = None
        self.sky = None
        self.firstPerson = CameraShyFirstPerson(self)
        self.skyUtil = None
        self.pbpText = None

    def generateOtherPlayerGui(self):
        self.headPanels.generateOtherPlayerGui()

    def updateOtherPlayerHead(self, avId, otherAvId, state):
        self.headPanels.updateOtherPlayerHead(avId, otherAvId, state)

    def getPlayByPlayText(self):
        return OnscreenText(text = "", fg = (1, 1, 1, 1), shadow = (0, 0, 0, 1), pos = (0, 0.75))

    def removePlayByPlay(self):
        if self.pbpText:
            taskMgr.remove('DCameraShyGame-removePlayByPlay')
            self.pbpText.destroy()
            self.pbpText = None

    def removePlayByPlayTask(self, task):
        self.removePlayByPlay()
        return Task.done

    def showPlayByPlay(self, situation, avId):
        self.removePlayByPlay()
        av = self.cr.doId2do.get(avId)
        name = av.getName()
        if situation == 0:
            self.pbpText = self.getPlayByPlayText()
            self.pbpText.setText("{0} took a picture of you!".format(name))
        taskMgr.doMethodLater(3.0, self.removePlayByPlayTask, "DCameraShyGame-removePlayByPlay")

    def tookPictureOfMe(self, avId):
        self.headPanels.hideFrames()
        self.firstPerson.stopCameraFlash()
        base.transitions.setFadeColor(1, 1, 1)
        base.transitions.fadeOut(0.1)
        self.showPlayByPlay(0, avId)
        Sequence(Wait(1), Func(self.respawn)).start()

    def respawn(self):
        base.transitions.fadeIn()
        pos, hpr = self.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr - (180, 0, 0))
        base.localAvatar.d_broadcastPositionNow()
        Sequence(Wait(0.6), Func(self.headPanels.showFrames), Func(base.transitions.setFadeColor, 0, 0, 0)).start()

    def announceGameOver(self):
        self.fsm.request('announceGameOver')

    def showWinner(self, avId):
        base.transitions.fadeOut()
        Sequence(Wait(0.51), Func(self.fsm.request, 'showWinner', [avId])).start()
        #self.fsm.request('showWinner', [avId])

    def enterGameOver(self, winner, winnerDoId, allPrize):
        try:
            currentCamPos = base.camera.getPos(render)
            currentCamHpr = base.camera.getHpr(render)
            self.firstPerson.reallyEnd()
            base.camera.setPos(currentCamPos)
            base.camera.setHpr(currentCamHpr)
        except:
            pass
        DistributedMinigame.enterGameOver(self, winner, winnerDoId, allPrize)

    def enterShowWinner(self, winnerId):
        self.firstPerson.reallyEnd()
        avatar = self.getRemoteAvatar(winnerId)
        avatar.avatar.loop('neutral')
        avatar.detachCamera()
        self.thisPlayerWinsLbl = OnscreenText(text = "{0} Wins!".format(avatar.avatar.getName()), fg = (1, 1, 1, 1),
            font = CIGlobals.getMinnieFont(), pos = (0, 0.8), scale = 0.1)
        if winnerId == base.localAvatar.doId:
            self.thisPlayerWinsLbl.setText("You Win!")
        base.camera.reparentTo(avatar.avatar)
        base.camera.setPos(0, 7, 3)
        base.camera.setH(180)
        base.transitions.fadeIn()
        Sequence(Wait(0.5), Func(avatar.doWinDance)).start()

    def exitShowWinner(self):
        pass

    def enterAnnounceGameOver(self):
        whistle = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.mp3")
        base.playSfx(whistle)
        self.gameOverLbl = OnscreenText(text = 'Game Over!', fg = (1, 1, 1, 1), font = CIGlobals.getMinnieFont(), scale = 0.1)
        self.gameOverScaleIval = LerpScaleInterval(
            self.gameOverLbl,
            duration = 1.0,
            scale = 0.1,
            startScale = 0.0,
            blendType = 'easeOut'
        )
        #self.gameOverScaleIval.start()

    def exitAnnounceGameOver(self):
        self.gameOverScaleIval.finish()
        del self.gameOverScaleIval
        self.gameOverLbl.destroy()
        del self.gameOverLbl

    def remoteAvatarTakePicture(self, avId):
        avatar = self.getRemoteAvatar(avId)
        if avatar:
            avatar.takePicture()

    def standingAvatar(self, avId):
        avatar = self.getRemoteAvatar(avId)
        if avatar:
            avatar.stand()

    def runningAvatar(self, avId):
        avatar = self.getRemoteAvatar(avId)
        if avatar:
            avatar.run()

    def createRemoteAvatar(self, avId):
        if avId == base.localAvatar.doId:
            self.myRemoteAvatar = RemoteCameraShyAvatar(self, self.cr, avId)
            self.remoteAvatars.append(self.myRemoteAvatar)
        else:
            av = RemoteCameraShyAvatar(self, self.cr, avId)
            av.stand()
            self.remoteAvatars.append(av)

    def getRemoteAvatar(self, avId):
        for avatar in self.remoteAvatars:
            if avatar.avId == avId:
                return avatar

    def allPlayersReady(self):
        self.fsm.request('countdown')

    def enterCountdown(self):
        base.localAvatar.chatInput.disableKeyboardShortcuts()
        base.localAvatar.disableChatInput()
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        base.render.show()
        self.playMinigameMusic()
        self.countdownLbl = OnscreenText(text = "", fg = (1, 1, 1, 1), font = CIGlobals.getMinnieFont(), scale = 0.1)
        self.countdownTrack = Sequence(
            Func(self.countdownLbl.setText, "5"),
            Wait(1.0),
            Func(self.countdownLbl.setText, "4"),
            Wait(1.0),
            Func(self.countdownLbl.setText, "3"),
            Wait(1.0),
            Func(self.countdownLbl.setText, "2"),
            Wait(1.0),
            Func(self.countdownLbl.setText, "1"),
            Wait(1.0),
            Func(self.fsm.request, "play")
        )
        self.countdownTrack.start()
        self.firstPerson.start()
        self.firstPerson.disableMouse()

    def exitCountdown(self):
        if hasattr(self, 'countdownTrack'):
            self.countdownTrack.pause()
            del self.countdownTrack
        if hasattr(self, 'countdownLbl'):
            self.countdownLbl.destroy()
            del self.countdownLbl

    def enterPlay(self):
        self.createTimer()
        self.firstPerson.reallyStart()

    def exitPlay(self):
        self.firstPerson.end()
        self.firstPerson.enableMouse()
        self.deleteTimer()
        base.localAvatar.createChatInput()
        base.localAvatar.chatInput.enableKeyboardShortcuts()
        DistributedMinigame.exitPlay(self)

    def createWorld(self):
        self.deleteWorld()
        self.maze = loader.loadModel("phase_4/models/minigames/maze_1player.bam")
        self.maze.find('**/maze_walls').setSz(1.5)
        self.maze.reparentTo(base.render)
        self.mazeCollModel = loader.loadModel("phase_4/models/minigames/maze_1player_collisions.egg")
        self.mazeCollModel.reparentTo(base.render)
        self.mazeCollModel.hide()
        self.mazeCollModel.setTransparency(1)
        self.mazeCollModel.setColorScale(1, 1, 1, 0)
        for node in self.mazeCollModel.findAllMatches('**'):
            node.setSz(1.5)
        self.sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
        self.skyUtil = SkyUtil()
        self.skyUtil.startSky(self.sky)
        self.sky.reparentTo(base.camera)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)
        self.spawnPoints.append((Point3(0, 0, 0), Vec3(0, 0, 0)))
        self.spawnPoints.append((Point3(-23.89, 18.58, 0.00), Vec3(90.00, 0.00, 0.00)))
        self.spawnPoints.append((Point3(-23.89, 6.30, 0.00), Vec3(0.00, 0.00, 0.00)))
        self.spawnPoints.append((Point3(23.78, 6.30, 0.00), Vec3(0.00, 0.00, 0.00)))
        self.spawnPoints.append((Point3(8.12, -17.79, 0.00), Vec3(270.00, 0.00, 0.00)))

    def deleteWorld(self):
        if self.maze:
            self.maze.removeNode()
            self.maze = None
        if self.mazeCollModel:
            self.mazeCollModel.removeNode()
            self.mazeCollModel = None
        if self.skyUtil:
            self.skyUtil.stopSky()
            self.skyUtil = None
        if self.sky:
            self.sky.removeNode()
            self.sky = None

    def pickSpawnPoint(self):
        return random.choice(self.spawnPoints)

    def setSpawnPoint(self, index):
        pos, hpr = self.spawnPoints[index]
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)

    def load(self):
        self.createWorld()
        self.setMinigameMusic("phase_6/audio/bgm/GS_Race_SS.mid")
        self.setDescription("Be the first to take 3 pictures of all the other Toons with your camera. " + \
            "Use WASD to move and the mouse to look around. Press the left mouse button to take a picture. " + \
            "Your camera takes some time to recharge after taking a picture. " + \
            "You know you have a good shot when the view finder is green!")
        self.setWinnerPrize(30)
        self.setLoserPrize(15)
        base.render.hide()
        base.setBackgroundColor(0, 0, 0)
        DistributedMinigame.load(self)

    def announceGenerate(self):
        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))
        self.load()
        DistributedMinigame.announceGenerate(self)

    def disable(self):
        if self.thisPlayerWinsLbl:
            self.thisPlayerWinsLbl.destroy()
            self.thisPlayerWinsLbl = None
        base.camera.reparentTo(render)
        base.camera.setPos(0, 0, 0)
        base.camera.setHpr(0, 0, 0)
        if self.myRemoteAvatar:
            self.myRemoteAvatar.cleanup()
            del self.myRemoteAvatar
        self.firstPerson.cleanup()
        del self.firstPerson
        self.deleteWorld()
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        DistributedMinigame.disable(self)

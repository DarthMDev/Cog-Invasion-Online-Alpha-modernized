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
from lib.coginvasion.gui.Whisper import Whisper
from lib.coginvasion.minigame.GunGameToonFPS import GunGameToonFPS
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
from DistributedToonFPSGame import DistributedToonFPSGame
import GunGameLevelLoader
import GunGameGlobals as GGG

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
        self.fsm.addState(State('voteGM', self.enterVoteGameMode, self.exitVoteGameMode, ['chooseTeam']))
        self.fsm.addState(State('chooseTeam', self.enterChooseTeam, self.exitChooseTeam, ['chooseGun']))
        self.fsm.addState(State('chooseGun', self.enterChooseGun, self.exitChooseGun, ['waitForOthers']))
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.fsm.getStateNamed('play').addTransition('announceGameOver')
        self.toonFps = GunGameToonFPS(self)
        self.loader = GunGameLevelLoader.GunGameLevelLoader()
        self.track = None
        self.isTimeUp = False
        self.cameraMovmentSeq = None
        self.gameMode = None
        self.team = None
        self.balloonSound = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.mp3')
        self.decidedSound = base.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_win_vote.mp3')
        return

    def enterVoteGameMode(self):
        font = CIGlobals.getMickeyFont()
        imp = CIGlobals.getToonFont()
        box = DGG.getDefaultDialogGeom()
        geom = CIGlobals.getDefaultBtnGeom()
        self.container = DirectFrame()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4),
            parent = self.container)
        self.title = OnscreenText(
            text = "Vote  on  Game  Mode", pos = (0, 0.5, 0), font = font,
            scale = (0.12), parent = self.container, fg = (1, 0.9, 0.3, 1))
        self.btnFrame = DirectFrame(parent = self.container, pos = (0.14, 0, 0))
        self.casualFrame = DirectFrame(parent = self.btnFrame, pos = (-0.5, 0, 0))
        self.ctfFrame = DirectFrame(parent = self.btnFrame, pos = (0.22, 0, 0))
        self.casual = DirectButton(
        	parent = self.casualFrame, relief = None, pressEffect = 0,
        	image = ('phase_4/maps/casual_neutral.png',
        			'phase_4/maps/casual_hover.png',
        			'phase_4/maps/casual_hover.png'),
        	image_scale = (0.9, 1, 1), scale = 0.4, command = self.__pickedGameMode, extraArgs = [GGG.GameModes.CASUAL])
        self.casual_votesLbl = OnscreenText(
        	parent = casualFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.ctf = DirectButton(
        	parent = self.ctfFrame, relief = None, pressEffect = 0,
        	image = ('phase_4/maps/ctf_neutral.png',
        			'phase_4/maps/ctf_hover.png',
        			'phase_4/maps/ctf_hover.png'),
        	image_scale = (0.9, 1, 1), scale = 0.4, command = self.__pickedGameMode, extraArgs = [GGG.GameModes.CTF])
        self.ctf_votesLbl = OnscreenText(
        	parent = self.ctfFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.outcomeLbl = OnscreenText(
        	parent = self.container, text = "", pos = (0, -0.6, 0), font = imp, scale = 0.1)

    def __pickedGameMode(self, mode):
        self.sendUpdate('myGameModeVote', [mode])
        self.ctf['state'] = DGG.DISABLED
        self.casual['state'] = DGG.DISABLED

    def incrementGameModeVote(self, mode):
        base.playSfx(self.balloonSound)
        lbl = None
        if mode == GGG.GameModes.CTF:
            lbl = self.ctf_votesLbl
        elif mode == GGG.GameModes.CASUAL:
            lbl = self.casual_votesLbl
        if lbl:
            lbl.setText(str(int(lbl.getText()) + 1))

    def gameModeDecided(self, mode, wasRandom):
        base.playSfx(self.decidedSound)
        if wasRandom:
            msg = GGG.MSG_CHOSE_MODE_TIE.format(GGG.GameModeNameById[mode])
        else:
            msg = GGG.MSG_CHOSE_MODE.format(GGG.GameModeNameById[mode])
        self.outcomeLbl.setText(msg)

    def exitVoteGameMode(self):
        self.outcomeLbl.destroy()
        del self.outcomeLbl
        self.ctf_votesLbl.destroy()
        del self.ctf_votesLbl
        self.casual_votesLbl.destroy()
        del self.casual_votesLbl
        self.ctf.destroy()
        del self.ctf
        self.casual.destroy()
        del self.casual
        self.ctfFrame.destroy()
        del self.ctfFrame
        self.casualFrame.destroy()
        del self.casualFrame
        self.title.destroy()
        del self.title
        self.bg.destroy()
        del self.bg
        self.container.destroy()
        del self.container

    def enterChooseTeam(self):
        font = CIGlobals.getMickeyFont()
        box = loader.loadModel('phase_3/models/gui/dialog_box_gui.bam')
        imp = CIGlobals.getToonFont()
        geom = CIGlobals.getDefaultBtnGeom()
        self.container = DirectFrame()
        self.bg = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4),
        	parent = self.container)
        self.title = OnscreenText(
        	text = "Join  a  Team", pos = (0, 0.5, 0), font = font,
        	scale = (0.12), parent = self.container, fg = (1, 0.9, 0.3, 1))
        self.btnFrame = DirectFrame(parent = self.container, pos = (0.14, 0, 0))
        self.bbsFrame = DirectFrame(parent = self.btnFrame, pos = (-0.5, 0, 0))
        self.rrbFrame = DirectFrame(parent = self.btnFrame, pos = (0.22, 0, 0))
        self.bbs = DirectButton(
        	parent = self.bbsFrame, relief = None, pressEffect = 0,
        	image = ('phase_4/maps/blue_neutral.png',
        			'phase_4/maps/blue_hover.png',
        			'phase_4/maps/blue_hover.png'),
        	image_scale = (0.9, 1, 1), scale = 0.4, command = self.__choseTeam, extraArgs = [GGG.Teams.BLUE])
        self.bbs_playersLbl = OnscreenText(
        	parent = self.bbsFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.rrb = DirectButton(
        	parent = self.rrbFrame, relief = None, pressEffect = 0,
        	image = ('phase_4/maps/red_neutral.png',
        			'phase_4/maps/red_hover.png',
        			'phase_4/maps/red_hover.png'),
        	image_scale = (0.9, 1, 1), scale = 0.4, command = self.__choseTeam, extraArgs = [GGG.Teams.RED])
        self.rrb_playersLbl = OnscreenText(
        	parent = self.rrbFrame, text = "0", pos = (0, -0.46, 0), font = imp)
        self.teamFull_text = OnscreenText(
            parent = self.container, text = "", pos = (0, -0.6, 0), font = imp)

    def __choseTeam(self, team):
        self.team = team
        self.bbs['state'] = DGG.DISABLED
        self.rrb['state'] = DGG.DISABLED
        self.sendUpdate('choseTeam', [team])

    def teamFull(self):
        # Oh, man, the team is full. Let's try again.
        self.teamFull_text.setText('Sorry, that team is full.')
        self.team = None
        self.bbs['state'] = DGG.NORMAL
        self.rrb['state'] = DGG.NORMAL

    def acceptedIntoTeam(self):
        # Yay, we're on the team! Let's choose our gun!
        Whisper().createSystemMessage(GGG.MSG_WELCOME.format(GGG.TeamNameById[self.team]))
        self.fsm.request('chooseGun')

    def incrementTeamPlayers(self, team):
        if team == GGG.Teams.RED:
            lbl = self.rrb_playersLbl
        elif team == GGG.Teams.BLUE:
            lbl = self.bbs_playersLbl
        lbl.setText(str(int(lbl.getText()) + 1))

    def exitChooseTeam(self):
        self.teamFull_text.destroy()
        del self.teamFull_text
        self.rrb_playersLbl.destroy()
        del self.rrb_playersLbl
        self.bbs_playersLbl.destroy()
        del self.casual_votesLbl
        self.rrb.destroy()
        del self.ctf
        self.bbs.destroy()
        del self.casual
        self.rrbFrame.destroy()
        del self.rrbFrame
        self.bbsFrame.destroy()
        del self.bbsFrame
        self.title.destroy()
        del self.title
        self.bg.destroy()
        del self.bg
        self.container.destroy()
        del self.container

    def setTeamOfPlayer(self, avId, team):
        remoteAvatar = self.getRemoteAvatar(avId)
        if remoteAvatar:
            remoteAvatar.setTeam(team)

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
        self.sendUpdate('readyToStart')
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

    def setupRemoteAvatar(self, avId):
        self.remoteAvatars.append(RemoteToonBattleAvatar(self, self.cr, avId))

    def setLevelName(self, levelName):
        self.loader.setLevel(levelName)
        self.loader.load()
        pos, hpr = self.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)

    def pickSpawnPoint(self):
        return random.choice(self.loader.getSpawnPoints())

    def load(self):
        self.toonFps.load()
        self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
        self.setMinigameMusic("phase_4/audio/bgm/MG_TwoDGame.mid")
        self.setDescription("Battle and defeat the other Toons with your gun to gain points. " + \
                            "Remember to reload your gun when you're out of ammo! " + \
                            "The Toon with the most points when the timer runs out gets a nice prize!")
        self.setWinnerPrize(70)
        self.setLoserPrize(15)
        #pos, hpr = self.loader.getCameraOfCurrentLevel()
        #camera.setPos(pos)
        #camera.setHpr(hpr)
        DistributedToonFPSGame.load(self)

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

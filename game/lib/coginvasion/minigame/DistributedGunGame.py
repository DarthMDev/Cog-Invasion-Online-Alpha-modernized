"""

  Filename: DistributedGunGame.py
  Created by: blach (26Oct14)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from lib.coginvasion.globals import CIGlobals, ChatGlobals
from lib.coginvasion.gui.WhisperPopup import WhisperPopup
from lib.coginvasion.minigame.GunGameToonFPS import GunGameToonFPS
from RemoteToonBattleAvatar import RemoteToonBattleAvatar
from DistributedToonFPSGame import DistributedToonFPSGame
import GunGameLevelLoader
import GunGameGlobals as GGG

import random
import math

class DistributedGunGame(DistributedToonFPSGame):
    notify = directNotify.newCategory("DistributedGunGame")
    GameMode2Description = {GGG.GameModes.CASUAL: "Battle and defeat the Toons on the other team with your gun to gain points. " + \
                        "Remember to reload your gun when you're out of ammo! " + \
                        "The Toon with the most points when the timer runs out gets a nice prize!",
                        GGG.GameModes.CTF: "Steal the other team's flag and take it to where your flag is to score a point. Follow the arrows at the bottom of the screen to find the flags! Use your gun to defend yourself and your flag!"}
    GameMode2Music = {GGG.GameModes.CASUAL: 'phase_4/audio/bgm/MG_TwoDGame.mid',
                      GGG.GameModes.CTF:    'phase_9/audio/bgm/CHQ_FACT_bg.mid'}

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
        self.fsm.addState(State('voteGM', self.enterVoteGameMode, self.exitVoteGameMode, ['start']))
        self.fsm.addState(State('chooseTeam', self.enterChooseTeam, self.exitChooseTeam, ['chooseGun']))
        self.fsm.addState(State('chooseGun', self.enterChooseGun, self.exitChooseGun, ['waitForOthers']))
        self.fsm.addState(State('announceTeamWon', self.enterAnnounceTeamWon, self.exitAnnounceTeamWon, ['finalScores']))
        self.fsm.getStateNamed('waitForOthers').addTransition('countdown')
        self.fsm.getStateNamed('waitForOthers').addTransition('voteGM')
        self.fsm.getStateNamed('play').addTransition('announceGameOver')
        self.fsm.getStateNamed('play').addTransition('announceTeamWon')
        self.fsm.getStateNamed('start').addTransition('chooseTeam')
        self.toonFps = GunGameToonFPS(self)
        self.loader = GunGameLevelLoader.GunGameLevelLoader(self)
        self.track = None
        self.isTimeUp = False
        self.cameraMovmentSeq = None
        self.gameMode = None
        self.team = None
        self.flags = []
        self.localAvHasFlag = False
        self.blueScoreLbl = None
        self.redScoreLbl = None
        self.redArrow = None
        self.blueArrow = None
        self.infoLbl = None
        self.scoreByTeam = {GGG.Teams.RED: 0, GGG.Teams.BLUE: 0}
        self.playersByTeam = {GGG.Teams.RED: 0, GGG.Teams.BLUE: 0}
        self.balloonSound = base.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.mp3')
        self.decidedSound = base.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_win_vote.mp3')
        return

    def getFlagOfOtherTeam(self, team):
        for flag in self.flags:
            if flag.team != team:
                return flag

    def startGameModeVote(self):
        self.fsm.request('voteGM')

    def enterVoteGameMode(self):
        render.hide()
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
        	parent = self.casualFrame, text = "0", pos = (0, -0.46, 0), font = imp)
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
        if mode == GGG.GameModes.CASUAL:
            self.ctf['image'] = 'phase_4/maps/ctf_neutral.png'
            self.casual['image'] = 'phase_4/maps/casual_hover.png'
        elif mode == GGG.GameModes.CTF:
            self.ctf['image'] = 'phase_4/maps/ctf_hover.png'
            self.casual['image'] = 'phase_4/maps/casual_neutral.png'

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
        base.taskMgr.doMethodLater(3.0, self.__decided2chooseTeamTask, self.uniqueName('decided2chooseTeamTask'))

    def __decided2chooseTeamTask(self, task):
        self.fsm.request('start')
        return task.done

    def exitVoteGameMode(self):
        base.taskMgr.remove(self.uniqueName('decided2chooseTeamTask'))
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
        	parent = self.bbsFrame, text = str(self.playersByTeam[GGG.Teams.BLUE]), pos = (0, -0.46, 0), font = imp)
        self.rrb = DirectButton(
        	parent = self.rrbFrame, relief = None, pressEffect = 0,
        	image = ('phase_4/maps/red_neutral.png',
        			'phase_4/maps/red_hover.png',
        			'phase_4/maps/red_hover.png'),
        	image_scale = (0.9, 1, 1), scale = 0.4, command = self.__choseTeam, extraArgs = [GGG.Teams.RED])
        self.rrb_playersLbl = OnscreenText(
        	parent = self.rrbFrame, text = str(self.playersByTeam[GGG.Teams.RED]), pos = (0, -0.46, 0), font = imp)
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
        message = GGG.MSG_WELCOME.format(GGG.TeamNameById[self.team])
        whisper = WhisperPopup(message, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)
        self.fsm.request('chooseGun')
        pos, hpr = self.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)

    def incrementTeamPlayers(self, team):
        self.playersByTeam[team] += 1
        if self.fsm.getCurrentState().getName() == 'chooseTeam':
            if team == GGG.Teams.RED:
                lbl = self.rrb_playersLbl
            elif team == GGG.Teams.BLUE:
                lbl = self.bbs_playersLbl
            lbl.setText(str(self.playersByTeam[team]))

    def exitChooseTeam(self):
        self.teamFull_text.destroy()
        del self.teamFull_text
        self.rrb_playersLbl.destroy()
        del self.rrb_playersLbl
        self.bbs_playersLbl.destroy()
        del self.bbs_playersLbl
        self.rrb.destroy()
        del self.rrb
        self.bbs.destroy()
        del self.bbs
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
        self.sniperBtn = DirectButton(geom = geom, text = "Sniper", relief = None, text_scale = 0.055, text_pos = (0, -0.01),
            command = self.__gunChoice, extraArgs = ["sniper"], pos = (0, 0, 0.15), parent = self.container)			

    def __gunChoice(self, choice):
        self.toonFps.cleanup()
        self.toonFps = None
        self.toonFps = GunGameToonFPS(self, choice)
        self.toonFps.load()
        self.sendUpdate('readyToStart')
        self.fsm.request('waitForOthers')

    def exitChooseGun(self):
        self.sniperBtn.destroy()
        del self.sniperBtn		
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
        self.setDescription(self.GameMode2Description[mode])
        self.setMinigameMusic(self.GameMode2Music[mode])

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

    def pickSpawnPoint(self):
        return random.choice(self.loader.getSpawnPoints())

    def load(self):
        self.toonFps.load()
        self.myRemoteAvatar = RemoteToonBattleAvatar(self, self.cr, base.localAvatar.doId)
        self.setWinnerPrize(200)
        self.setLoserPrize(15)
        
        if not base.localAvatar.tokenIcon is None:
            base.localAvatar.tokenIcon.hide()
        
        #pos, hpr = self.loader.getCameraOfCurrentLevel()
        #camera.setPos(pos)
        #camera.setHpr(hpr)
        DistributedToonFPSGame.load(self, showDesc = False)
        DistributedToonFPSGame.handleDescAck(self)

    def handleDescAck(self):
        self.fsm.request('chooseTeam')

    def incrementKills(self):
        self.toonFps.killedSomebody()

    def allPlayersReady(self):
        self.fsm.request('countdown')

    def timeUp(self):
        if not self.isTimeUp:
            self.fsm.request('announceGameOver')
            self.isTimeUp = True

    def teamWon(self, team):
        self.fsm.request('announceTeamWon', [team])

    def enterAnnounceTeamWon(self, team):
        whistleSfx = base.loadSfx("phase_4/audio/sfx/AA_sound_whistle.mp3")
        whistleSfx.play()
        del whistleSfx
        text = GGG.TeamNameById[team].split(' ')[0]
        self.gameOverLbl = DirectLabel(text = "{0}\nWins!".format(text), relief = None, scale = 0.35, text_font = CIGlobals.getMickeyFont(), text_fg = (1, 0, 0, 1))
        self.track = Sequence(Wait(3.0), Func(self.fsm.request, 'finalScores'))
        self.track.start()

    def exitAnnounceTeamWon(self):
        self.gameOverLbl.destroy()
        del self.gameOverLbl
        if self.track:
            self.track.pause()
            self.track = None

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

    def incrementTeamScore(self, team):
        self.scoreByTeam[team] += 1
        if team == GGG.Teams.BLUE:
            self.blueScoreLbl.setText("Blue: {0}".format(self.scoreByTeam[team]))
        elif team == GGG.Teams.RED:
            self.redScoreLbl.setText('Red: {0}'.format(self.scoreByTeam[team]))

    def __updateArrows(self, task):
        blueFlag = None
        redFlag = None

        for flag in self.flags:
            if flag.team == GGG.Teams.BLUE:
                blueFlag = flag
            if flag.team == GGG.Teams.RED:
                redFlag = flag

        if not blueFlag or not redFlag:
            return task.done

        bLocation = blueFlag.flagMdl.getPos(base.cam)
        bRotation = base.cam.getQuat(base.cam)
        bCamSpacePos = bRotation.xform(bLocation)
        bArrowRadians = math.atan2(bCamSpacePos[0], bCamSpacePos[1])
        bArrowDegrees = (bArrowRadians/math.pi) * 180
        self.blueArrow.setR(bArrowDegrees - 90)

        rLocation = redFlag.flagMdl.getPos(base.cam)
        rRotation = base.cam.getQuat(base.cam)
        rCamSpacePos = rRotation.xform(rLocation)
        rArrowRadians = math.atan2(rCamSpacePos[0], rCamSpacePos[1])
        rArrowDegrees = (rArrowRadians/math.pi) * 180
        self.redArrow.setR(rArrowDegrees - 90)

        return task.cont

    def enterCountdown(self):
        render.show()
        if self.gameMode == GGG.GameModes.CTF:
            self.blueScoreLbl = OnscreenText(text = "Blue: 0", scale = 0.1, pos = (-0.1, -0.85),
                fg = GGG.TeamColorById[GGG.Teams.BLUE], shadow = (0,0,0,1), align = TextNode.ARight)
            self.blueArrow = loader.loadModel('phase_3/models/props/arrow.bam')
            self.blueArrow.setColor(GGG.TeamColorById[GGG.Teams.BLUE])
            self.blueArrow.reparentTo(aspect2d)
            self.blueArrow.setPos(-0.2, 0, -0.7)
            self.blueArrow.setScale(0.1)
            self.redScoreLbl = OnscreenText(text = "Red: 0", scale = 0.1, pos = (0.1, -0.85),
                fg = GGG.TeamColorById[GGG.Teams.RED], shadow = (0,0,0,1), align = TextNode.ALeft)
            self.redArrow = loader.loadModel('phase_3/models/props/arrow.bam')
            self.redArrow.setColor(GGG.TeamColorById[GGG.Teams.RED])
            self.redArrow.reparentTo(aspect2d)
            self.redArrow.setPos(0.2, 0, -0.7)
            self.redArrow.setScale(0.1)
            self.infoLbl = OnscreenText(text = "Playing to: 3", scale = 0.1, pos = (0, -0.95),
                fg = (1, 1, 1, 1), shadow = (0,0,0,1))
            base.taskMgr.add(self.__updateArrows, self.uniqueName('updateArrows'))
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
        DistributedToonFPSGame.exitPlay(self)

    def announceGenerate(self):
        DistributedToonFPSGame.announceGenerate(self)
        base.localAvatar.walkControls.setWalkSpeed(GGG.ToonForwardSpeed, GGG.ToonJumpForce,
                                                   GGG.ToonReverseSpeed, GGG.ToonRotateSpeed)
        self.load()
        base.camLens.setMinFov(CIGlobals.GunGameFOV / (4./3.))

    def disable(self):
        render.show()
        base.localAvatar.setWalkSpeedNormal()
        
        # Show the staff icon again.
        if not base.localAvatar.tokenIcon is None:
            base.localAvatar.tokenIcon.show()
        
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.taskMgr.remove(self.uniqueName('updateArrows'))
        self.playersByTeam = None
        if self.blueArrow:
            self.blueArrow.removeNode()
            self.blueArrow = None
        if self.redArrow:
            self.redArrow.removeNode()
            self.redArrow = None
        if self.blueScoreLbl:
            self.blueScoreLbl.destroy()
            self.blueScoreLbl = None
        if self.redScoreLbl:
            self.redScoreLbl.destroy()
            self.redScoreLbl = None
        if self.infoLbl:
            self.infoLbl.destroy()
            self.infoLbl = None
        self.scoreByTeam = None
        self.flags = None
        self.gameMode = None
        self.team = None
        self.localAvHasFlag = None
        if self.loader:
            self.loader.unload()
            self.loader.cleanup()
            self.loader = None
        self.isTimeUp = None
        self.toonFps.reallyEnd()
        self.toonFps.cleanup()
        self.toonFps = None
        self.spawnPoints = None
        DistributedToonFPSGame.disable(self)

"""

  Filename: DistributedSuitManager.py
  Created by: blach (22Dec14)

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals, ChatGlobals
from lib.coginvasion.gui.WhisperPopup import WhisperPopup
from lib.coginvasion.suit.CogTournamentMusicManager import CogTournamentMusicManager
import random

#import ccoginvasion

class DistributedSuitManager(DistributedObject):
    notify = directNotify.newCategory("DistributedSuitManager")

    def __init__(self, cr):
        try:
            self.DistributedSuitManager_initialized
            return
        except:
            self.DistributedSuitManager_initialized = 1
        DistributedObject.__init__(self, cr)
        #self.musicMgr = ccoginvasion.CTMusicManager()
        self.hood = cr.playGame.hood
        self.spawnerStatus = 0
        return

    def spawner(self, onOrOff):
        self.spawnerStatus = bool(onOrOff)
        if self.cr.playGame.getPlace():
            self.cr.playGame.getPlace().maybeUpdateAdminPage()

    def getSpawner(self):
        return self.spawnerStatus

    def d_requestSuitInfo(self):
        self.notify.info("sending update 'requestSuitInfo'")
        self.sendUpdate('requestSuitInfo', [])

    def systemMessage(self, message):
        whisper = WhisperPopup('Toon HQ: ' + message, CIGlobals.getToonFont(), ChatGlobals.WTSystem)
        whisper.manage(base.marginManager)

    def noSuits(self):
        self.notify.info("There are no suits!")
        if not hasattr(self.hood, 'loader'):
            return
        if self.hood.loader.music.status() == self.hood.loader.music.READY:
            self.notify.info('playing noSuits music.')
            if self.hood.loader.battleMusic:
                self.hood.loader.battleMusic.stop()
            if self.hood.loader.invasionMusic:
                self.hood.loader.invasionMusic.stop()
            if self.hood.loader.tournamentMusic:
                self.hood.loader.tournamentMusic.stop()
                base.cr.music = None
            #self.musicMgr.stop_clip()
            self.hood.loader.bossBattleMusic.stop()
            base.playMusic(self.hood.loader.music, looping = 1, volume = 0.9)
        #self.hood.stopSuitEffect()

    def newSuit(self):
        self.notify.info("There are active Suits!")
        if not hasattr(self.hood, 'loader'):
            return
        if not self.hood.loader.battleMusic or self.hood.loader.battleMusic.status() == self.hood.loader.battleMusic.READY:
            self.notify.info('playing newSuit music.')
            self.hood.loader.music.stop()
            self.hood.loader.bossBattleMusic.stop()
            self.hood.loader.battleMusic.stop()
            if self.hood.loader.tournamentMusic:
                self.hood.loader.tournamentMusic.stop()
                self.hood.loader.tournamentMusic = None
            if self.hood.loader.invasionMusic:
                self.hood.loader.invasionMusic.stop()
                self.hood.loader.invasionMusic = None
            base.playMusic(self.hood.loader.battleMusic, looping = 1, volume = 0.9)
        #self.hood.startSuitEffect()

    def bossSpawned(self):
        if not hasattr(self.hood, 'loader'):
            return
        if not self.hood.loader.bossBattleMusic or self.hood.loader.bossBattleMusic.status() == self.hood.loader.bossBattleMusic.READY:
            self.notify.info('playing bossSpawned music.')
            self.hood.loader.music.stop()
            self.hood.loader.battleMusic.stop()
            if self.hood.loader.invasionMusic:
                self.hood.loader.invasionMusic.stop()
                self.hood.loader.invasionMusic = None
            if self.hood.loader.tournamentMusic:
                self.hood.loader.tournamentMusic.stop()
                self.hood.loader.tournamentMusic = None
                base.cr.music = None
            base.playMusic(self.hood.loader.bossBattleMusic, looping = 1, volume = 0.9)

    def invasionSpawned(self):
        if not hasattr(self.hood, 'loader'):
            return
        if not self.hood.loader.invasionMusic or self.hood.loader.invasionMusic.status() == self.hood.loader.invasionMusic.READY:
            self.notify.info('playing invasionSpawned music.')
            self.hood.loader.music.stop()
            self.hood.loader.bossBattleMusic.stop()
            self.hood.loader.battleMusic.stop()
            if self.hood.loader.tournamentMusic:
                self.hood.loader.tournamentMusic.stop()
            if self.hood.loader.invasionMusic:
                self.hood.loader.invasionMusic.stop()
            self.hood.loader.invasionMusic = None
            choice = random.choice(self.hood.loader.invasionMusicFiles)
            if "BossBot_CEO_v1" in choice:
                volume = 1.7
            else:
                volume = 0.9
            self.hood.loader.invasionMusic = base.loadMusic(choice)
            base.playMusic(self.hood.loader.invasionMusic, looping = 1, volume = volume)

    def tournamentSpawned(self):
        if not hasattr(self.hood, 'loader'):
            return
        if not self.hood.loader.tournamentMusic or self.hood.loader.tournamentMusic.status() == self.hood.loader.tournamentMusic.READY:
            self.hood.loader.music.stop()
            self.hood.loader.bossBattleMusic.stop()
            self.hood.loader.battleMusic.stop()
            if self.hood.loader.tournamentMusic:
                self.hood.loader.tournamentMusic.stop()
            if self.hood.loader.invasionMusic:
                self.hood.loader.invasionMusic.stop()
            self.hood.loader.tournamentMusic = None
            self.hood.loader.tournamentMusic = base.loadMusic(random.choice(self.hood.loader.tournamentMusicFiles))
            # Make .ogg music files base.cr.music so we can replay it when the window gets minimized and comes back.
            base.cr.music = self.hood.loader.tournamentMusic
            base.playMusic(self.hood.loader.tournamentMusic, looping = 1, volume = 0.9)
            #self.musicMgr.start_music()
            #base.accept('control-5', self.musicMgr.set_clip_request, ["5050_orchestra"])
            #base.accept('5', self.musicMgr.set_clip_request, ["5050_base"])
            #base.accept('control-l', self.musicMgr.set_clip_request, ["located_orchestra"])
            #base.accept('l', self.musicMgr.set_clip_request, ["located_base"])
            #base.accept('control-r', self.musicMgr.set_clip_request, ["running_away_orchestra"])
            #base.accept('r', self.musicMgr.set_clip_request, ["running_away_base"])
            #base.accept('control-g', self.musicMgr.set_clip_request, ["getting_worse_orchestra"])
            #base.accept('g', self.musicMgr.set_clip_request, ["getting_worse_base"])
            #base.accept('control-i', self.musicMgr.set_clip_request, ["intro_orchestra"])
            #base.accept('i', self.musicMgr.set_clip_request, ["intro_base"])
            #base.accept('shift-s', self.musicMgr.set_clip_request, ['static_cooldown'])
            #base.accept('a', self.musicMgr.set_clip_request, ["arresting_you"])
            #base.accept('h', self.musicMgr.set_clip_request, ["high_speed_cooldown_base"])
            #base.accept('control-h', self.musicMgr.set_clip_request, ["high_speed_cooldown_orchestra"])
            #base.accept('v', self.musicMgr.set_clip_request, ["very_low_speed_cooldown"])
            #base.accept('c', self.musicMgr.set_clip_request, ["low_speed_cooldown_1"])
            #base.accept('control-c', self.musicMgr.set_clip_request, ["low_speed_cooldown_2"])
            #base.accept('shift-a', self.musicMgr.set_clip_request, ["approaching_base"])
            #base.accept('shift-control-a', self.musicMgr.set_clip_request, ["approaching_orchestra"])
            #base.accept('control-a', self.musicMgr.set_clip_request, ["arrested_1"])
            #base.accept('e', self.musicMgr.set_clip_request, ["evaded_1"])
            #base.accept('f', self.musicMgr.set_clip_request, ["intro_orchestra_from_located"])

    def invasionInProgress(self):
        self.systemMessage(CIGlobals.SuitInvasionInProgMsg)

    def tournamentInProgress(self):
        self.systemMessage(CIGlobals.SuitTournamentInProgMsg)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        base.cr.playGame.suitManager = self

    def disable(self):
        base.cr.playGame.suitManager = None
        base.cr.music = None
        del self.hood
        del self.spawnerStatus
        DistributedObject.disable(self)

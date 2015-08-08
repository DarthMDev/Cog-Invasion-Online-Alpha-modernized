# Filename: CogTournamentMusicManager.py
# Created by:  blach (07Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.base.SectionedSound import AudioClip

import random

class CogTournamentMusicManager(DirectObject):
    notify = directNotify.newCategory("CogTournamentMusicManager")

    def __init__(self):
        self.suitsSpawnedInLastSomeSeconds = 0
        self.suitsKilledInLastSomeSeconds = 0
        self.index = random.choice(base.cr.tournamentMusicChunks.keys())
        self.clipNames = base.cr.tournamentMusicChunks[self.index]
        self.currentAudioClip = None

    def __handleClipDone(self):
        randomClips = ['located_orchestra', 'located_base', '5050_orchestra', '5050_base',
            'running_away_base', 'running_away_orchestra',
            'getting_worse_orchestra', 'getting_worse_base']
        newClip = random.choice(randomClips)
        self.playClip(newClip)

    def startMusic(self):
        baseOrOrch = random.choice(["base", "orchestra"])
        self.playClip("intro_" + baseOrOrch)
        self.accept('AudioClip_clipDone', self.__handleClipDone)

    def playClip(self, clipName):
        self.stopClip()

        ac = AudioClip(base.cr.tournamentMusicChunks[self.index][clipName])
        ac.playAllParts()
        self.currentAudioClip = ac

    def stopClip(self):
        if self.currentAudioClip:
            self.currentAudioClip.cleanup()
            self.currentAudioClip = None

    def cleanup(self):
        self.stopClip()
        self.suitsSpawnedInLastSomeSeconds = None
        self.suitsKilledInLastSomeSeconds = None
        self.index = None
        self.clipNames = None
        self.currentAudioClip = None

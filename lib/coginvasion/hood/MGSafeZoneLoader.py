"""

  Filename: MGSafeZoneLoader.py
  Created by: blach (05Jan15)

"""

from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import directNotify
import SafeZoneLoader
import MGPlayground
import random

class MGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    notify = directNotify.newCategory("MGSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = MGPlayground.MGPlayground
        self.pgMusicFilename = 'phase_13/audio/bgm/party_original_theme.mid'
        self.interiorMusicFilename = None
        self.battleMusicFile = None
        self.invasionMusicFiles = None
        self.tournamentMusicFiles = None
        self.bossBattleMusicFile = None
        self.dnaFile = 'phase_13/dna/party_sz.dna'
        self.szStorageDNAFile = 'phase_13/dna/storage_party_sz.dna'

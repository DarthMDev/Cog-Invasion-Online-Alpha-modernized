# Filename: TTTownLoader.py
# Created by:  blach (25Jul15)

import TownLoader
import TTStreet

class TTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.musicFile = 'phase_3.5/audio/bgm/TC_SZ.mid'
        self.interiorMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.mid'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_5/dna/toontown_central_' + str(self.branchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)

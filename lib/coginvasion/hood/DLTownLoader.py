# Filename: DLTownLoader.py
# Created by:  blach (26Jul15)

import TownLoader
import DLStreet

class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.musicFile = 'phase_8/audio/bgm/DL_SZ.mid'
        self.interiorMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.mid'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + str(self.branchZone) + '.dna'
        self.createHood(dnaFile)

# Filename: MLTownLoader.py
# Created by:  blach (26Jul15)

import TownLoader
import MLStreet

class MLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = MLStreet.MLStreet
        self.musicFile = 'phase_6/audio/bgm/MM_SZ.mid'
        self.interiorMusicFile = 'phase_6/audio/bgm/MM_SZ_activity.mid'
        self.townStorageDNAFile = 'phase_6/dna/storage_MM_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_6/dna/minnies_melody_land_' + str(self.branchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)

# Filename: TTSafeZoneLoader.py
# Created by:  blach (25Oct15)

from lib.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import TTPlayground

from lib.coginvasion.globals import CIGlobals

class TTSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = TTPlayground.TTPlayground
        self.pgMusicFilename = 'phase_4/audio/bgm/TC_nbrhood.ogg'
        self.interiorMusicFilename = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.battleMusicFile = 'phase_3.5/audio/bgm/encntr_general_bg.ogg'
        self.invasionMusicFiles = [
            "phase_12/audio/bgm/BossBot_CEO_v1.ogg",
            "phase_9/audio/bgm/encntr_suit_winning.ogg"
        ]
        self.tournamentMusicFiles = [
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_1.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_2.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_3.ogg",
            "phase_3.5/audio/bgm/encntr_nfsmw_bg_4.ogg",
        ]
        self.bossBattleMusicFile = 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg'
        self.dnaFile = 'phase_4/dna/new_ttc_sz.pdna'
        self.szStorageDNAFile = 'phase_4/dna/storage_TT_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_4/dna/winter_storage_TT_sz.pdna'
        self.telescope = None
        self.birdNoises = [
            'phase_4/audio/sfx/SZ_TC_bird1.ogg',
            'phase_4/audio/sfx/SZ_TC_bird2.ogg',
            'phase_4/audio/sfx/SZ_TC_bird3.ogg'
        ]
        self.trees = []

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.geom.find('**/ground_center').setBin('ground', 18)
        self.geom.find('**/ground_sidewalk').setBin('ground', 18)
        self.geom.find('**/ground').setBin('ground', 18)
        self.geom.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
        self.geom.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)
        #for face in self.geom.findAllMatches('**/ground_sidewalk_front_*'):
            #face.setColorScale(0.9, 0.9, 0.9, 1.0)
        for tunnel in self.geom.findAllMatches('**/linktunnel_tt*'):
            tunnel.find('**/tunnel_floor_1').setTexture(loader.loadTexture('phase_4/models/neighborhoods/tex/sidewalkbrown.jpg'), 1)
        for tree in self.geom.findAllMatches('**/prop_green_tree_*_DNARoot'):
            tree.wrtReparentTo(hidden)
            self.trees.append(tree)
            newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
            newShadow.reparentTo(tree)
            newShadow.setScale(1.5)
            newShadow.setColor(0, 0, 0, 0.5, 1)
        self.geom.flattenMedium()
        
    def unload(self):
        for tree in self.trees:
            tree.removeNode()
        self.trees = None
        SafeZoneLoader.SafeZoneLoader.unload(self)

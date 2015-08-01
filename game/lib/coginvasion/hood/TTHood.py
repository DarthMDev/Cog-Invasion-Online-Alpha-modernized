"""

  Filename: TTHood.py
  Created by: blach (01Dec14)

"""

import ToonHood
import TTSafeZoneLoader
import TTTownLoader
import SkyUtil
from lib.coginvasion.globals import CIGlobals
from pandac.PandaModules import *

class TTHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.ToontownCentral
        self.safeZoneLoader = TTSafeZoneLoader.TTSafeZoneLoader
        self.townLoader = TTTownLoader.TTTownLoader
        self.skyUtil = SkyUtil.SkyUtil()
        self.storageDNAFile = "phase_4/dna/storage_TT.dna"
        self.skyFilename = "phase_3.5/models/props/TT_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.loaderDoneEvent = 'TTHood-loaderDone'

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('TTHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TTHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, requestStatus):
        ToonHood.ToonHood.enter(self, requestStatus)

    def exit(self):
        ToonHood.ToonHood.exit(self)

    def startSuitEffect(self):
        ToonHood.ToonHood.startSuitEffect(self)
        if base.cr.playGame.getPlace():
            if hasattr(base.cr.playGame.getPlace(), 'stopBirds'):
                base.cr.playGame.getPlace().stopBirds()

    def stopSuitEffect(self, newSky = 1):
        if base.cr.playGame.getPlace():
            if hasattr(base.cr.playGame.getPlace(), 'startBirds'):
                base.cr.playGame.getPlace().startBirds()
        ToonHood.ToonHood.stopSuitEffect(self, newSky)

    def startSky(self):
        ToonHood.ToonHood.startSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.skyUtil.startSky(self.sky)

    def stopSky(self):
        ToonHood.ToonHood.stopSky(self)
        self.skyUtil.stopSky()

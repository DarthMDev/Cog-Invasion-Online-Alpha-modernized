# Filename: BRHood.py
# Created by:  blach (01Jul15)

from lib.coginvasion.globals import CIGlobals

import BRSafeZoneLoader
import BRTownLoader
import ToonHood

class BRHood(ToonHood.ToonHood):

	def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
		ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
		self.id = CIGlobals.TheBrrrgh
		self.safeZoneLoader = BRSafeZoneLoader.BRSafeZoneLoader
		self.townLoader = BRTownLoader.BRTownLoader
		self.storageDNAFile = "phase_8/dna/storage_BR.dna"
		self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
		self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
		self.titleColor = (0.25, 0.25, 1.0, 1.0)
		self.loaderDoneEvent = 'BRHood-loaderDone'

	def load(self):
		ToonHood.ToonHood.load(self)
		self.parentFSM.getStateNamed('BRHood').addChild(self.fsm)

	def unload(self):
		self.parentFSM.getStateNamed('BRHood').removeChild(self.fsm)
		ToonHood.ToonHood.unload(self)

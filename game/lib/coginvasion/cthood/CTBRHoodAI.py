# Filename: CTBRHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood import BRHoodAI
from lib.coginvasion.globals import CIGlobals

class CTBRHoodAI(BRHoodAI.BRHoodAI):
	notify = directNotify.newCategory("CTBRHoodAI")

	def __init__(self, air):
		BRHoodAI.BRHoodAI.__init__(self, air)
		self.startup()

	def startup(self):
		if 0:
			self.notify.info("Creating hood {0}...".format(CIGlobals.TheBrrrgh))
			self.dnaFiles = ['phase_8/dna/the_burrrgh_3100.pdna', 'phase_8/dna/the_burrrgh_3200.pdna',
	            'phase_8/dna/the_burrrgh_3300.pdna', 'phase_8/dna/the_burrrgh_sz.pdna']
			ToonHoodAI.ToonHoodAI.startup(self)
			#self.cogStation.b_setLocationPoint(1)
			self.notify.info("Finished creating hood %s" % CIGlobals.TheBrrrgh)

	def shutdown(self):
		if 0:
			self.notify.info("Shutting down hood %s" % CIGlobals.TheBrrrgh)
			ToonHoodAI.ToonHoodAI.shutdown(self)
			self.notify.info("Finished shutting down hood %s" % CIGlobals.TheBrrrgh)

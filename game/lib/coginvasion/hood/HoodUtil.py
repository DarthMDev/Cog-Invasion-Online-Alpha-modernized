"""

  Filename: HoodUtil.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.TTCHood import *
from lib.coginvasion.hood.HomeHood import *
from lib.coginvasion.gui.ToontownProgressScreen import ToontownProgressScreen
from panda3d.core import *
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from lib.coginvasion.hood.MinigameHood import *
from lib.coginvasion.hood import HoodGui

class HoodUtil(DirectObject):
	
	def __init__(self, cr = None):
		DirectObject.__init__(self)
		self.cr = cr
		self.centralHood = TTCHood(self.cr)
		self.homeHood = HomeHood()
		self.minigameHood = MinigameHood(self.cr)
		self.progressScreen = ToontownProgressScreen()
		
	def load(self, hood, AI = 0):
		if hood == "TT":
			if not AI:
				loader.beginBulkLoad(hood, CIGlobals.ToontownCentral, 20, 2, self.progressScreen)
			self.centralHood.createHood(AI = AI)
			self.setCurrentHood(self.centralHood)
			if not AI:
				loader.endBulkLoad(hood)
		elif hood == "home":
			if not AI:
				loader.beginBulkLoad(hood, CIGlobals.Estate, 20, 1, self.progressScreen)
			self.homeHood.createHood()
			self.setCurrentHood(self.homeHood)
			if not AI:
				loader.endBulkLoad(hood)
		elif hood == "minigamearea":
			if not AI:
				loader.beginBulkLoad(hood, CIGlobals.MinigameArea, 20, 3, self.progressScreen)
			self.minigameHood.createHood()
			self.setCurrentHood(self.minigameHood)
			if not AI:
				loader.endBulkLoad(hood)
		self.announceHood(hood)
		
	def setCurrentHood(self, hood):
		if self.cr is not None:
			self.cr.setCurrentHood(hood)
		
	def announceHood(self, hood):
		if hood == "TT":
			HoodGui.announceHood(CIGlobals.ToontownCentral)
		elif hood == "home":
			HoodGui.announceHood(CIGlobals.Estate)
		elif hood == "minigamearea":
			HoodGui.announceHood(CIGlobals.MinigameArea)
				
	def unload(self, hood):
		if hood == "TT":
			self.centralHood.unloadHood()
		elif hood == "home":
			self.homeHood.unloadHood()
		elif hood == "minigamearea":
			self.minigameHood.unloadHood()
			
	def enableSuitEffect(self, size):
		self.centralHood.enableSuitEffect(size)
		
	def disableSuitEffect(self):
		self.centralHood.disableSuitEffect()
	
			

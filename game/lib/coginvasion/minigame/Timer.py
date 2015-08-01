"""

  Filename: Timer.py
  Created by: blach (19Oct14)
  
"""

from panda3d.core import *
from direct.gui.DirectGui import *
from lib.coginvasion.globals import CIGlobals

class Timer:
	
	def __init__(self):
		try:
			self.Timer_initialized
			return
		except:
			self.Timer_initialized = 1
		self.timer = None
		self.timeLbl = None
		return
		
	def load(self):
		self.unload()
		timer = loader.loadModel("phase_3.5/models/gui/clock_gui.bam")
		self.timer = OnscreenImage(image=timer.find('**/alarm_clock'), pos=(-0.15, 0, -0.15), scale=0.4, parent=base.a2dTopRight)
		self.timeLbl = DirectLabel(text="0", parent=self.timer, text_scale=0.3, text_pos=(0, -0.13),
								text_font=CIGlobals.getMickeyFont(), text_fg=(1, 0, 0, 1),
								relief=None)
		timer.removeNode()
		self.timer.setBin('gui-popup', 60)
		del timer
		
	def unload(self):
		if self.timer:
			self.timer.destroy(); self.timer = None
		if self.timeLbl:
			self.timeLbl.destroy(); self.timeLbl = None
		
	def setTime(self, time):
		if self.timeLbl:
			self.timeLbl['text'] = str(time)
			if len(str(time)) > 2:
				self.timeLbl['text_scale'] = 0.2
				self.timeLbl['text_pos'] = (0, -0.11)
			else:
				self.timeLbl['text_scale'] = 0.3
				self.timeLbl['text_pos'] = (0, -0.13)

########################################
# Filename: DisplayOptions.py
# Created by: blach (??Jul14)
########################################

from lib.coginvasion.globals import CIGlobals
from panda3d.core import *
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from lib.coginvasion.manager.SettingsManager import SettingsManager

class DisplayOptions:
	
	def initializeWindow(self):
		width, height, fs, music, sfx, tex_detail, model_detail = SettingsManager().getSettings("settings.json")
		
		dialog_box = loader.loadModel("phase_3/models/gui/dialog_box_gui.bam")
		dialog_box_img = OnscreenImage(image=dialog_box, scale=(0.9, 0.75, 0.75))
		
		

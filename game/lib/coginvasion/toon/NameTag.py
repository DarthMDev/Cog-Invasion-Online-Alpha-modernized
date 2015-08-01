"""
  
  Filename: NameTag.py
  Created by: blach (??July14)
  
"""

from panda3d.core import *
from pandac.PandaModules import *
from direct.gui.DirectGui import *

class NameTag:
	
	def generate(self, name):
		tag = DirectLabel(text=name, text_fg=(0.191406, 0.5625, 0.773438, 1.0), text_bg=(0.75, 0.75, 0.75, 0.5), text_wordwrap=8, text_decal=True, relief=None, parent=hidden)
		tag.setBillboardPointEye()
		return tag

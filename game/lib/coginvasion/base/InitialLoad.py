"""

  Filename: InitialLoad.py
  Created by: blach (17June14)

"""

from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from direct.directnotify.DirectNotify import *
import FileUtility
from LoadUtility import LoadUtility
import glob

loadernotify = DirectNotify().newCategory("InitialLoad")

class InitialLoad(LoadUtility):

	def __init__(self, callback):
		LoadUtility.__init__(self, callback)
		phasesToScan = ["models", "phase_3/models"]
		self.models = FileUtility.findAllModelFilesInVFS(phasesToScan)
		self.version_lbl = None

	def createGui(self):
		self.version_lbl = OnscreenText(text="ver-" + game.version, scale=0.06, pos=(-1.32, -0.97, -0.97), align=TextNode.ALeft, fg=(0.9, 0.9, 0.9, 7))

	def load(self):
		loader.beginBulkLoad('init', 'init', len(self.models), 0, False)
		self.createGui()
		LoadUtility.load(self)

	def done(self):
		LoadUtility.done(self)
		loader.endBulkLoad('init')

	def destroy(self):
		self.version_lbl.destroy()
		self.version_lbl = None
		LoadUtility.destroy(self)

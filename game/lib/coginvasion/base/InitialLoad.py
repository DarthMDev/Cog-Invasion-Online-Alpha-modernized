########################################
# Filename: InitialLoad.py
# Created by: blach (17Jun14)
########################################

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
        self.clouds = None

    def createGui(self):
        self.version_lbl = OnscreenText(text="ver-" + game.version, scale=0.06, pos=(-1.32, -0.97, -0.97), align=TextNode.ALeft, fg=(0.343, 0.343, 0.343, 1))
        gui = loader.loadModel('phase_3/models/gui/loading-background.bam')
        gui.find('**/fg').removeNode()
        self.clouds = OnscreenImage(image = gui, parent = render2d)
        gui.removeNode()

    def load(self):
        loader.progressScreen.bg_img.hide()
        loader.progressScreen.bgm.hide()
        loader.progressScreen.bg.hide()
        loader.progressScreen.toontipFrame.hide()
        loader.progressScreen.logoNode.setPos(0, 0, 0)
        loader.progressScreen.logoNode.setScale(1.5)
        self.createGui()
        loader.beginBulkLoad('init', 'init', len(self.models), 0, False)
        LoadUtility.load(self)

    def done(self):
        LoadUtility.done(self)
        loader.endBulkLoad('init')

    def destroy(self):
        self.version_lbl.destroy()
        self.version_lbl = None
        self.clouds.destroy()
        self.clouds = None
        loader.progressScreen.bg_img.show()
        loader.progressScreen.bgm.show()
        loader.progressScreen.bg.show()
        loader.progressScreen.toontipFrame.show()
        loader.progressScreen.logoNode.setZ(loader.progressScreen.defaultLogoZ)
        loader.progressScreen.logoNode.setScale(loader.progressScreen.defaultLogoScale)
        LoadUtility.destroy(self)

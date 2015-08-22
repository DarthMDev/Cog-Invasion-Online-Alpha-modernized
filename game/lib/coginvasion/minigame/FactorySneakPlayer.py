# Filename: FactorySneakPlayer.py
# Created by:  blach (21Aug15)

from panda3d.core import Point3

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.gui.MoneyGui import MoneyGui
from FactorySneakGameToonFPS import FactorySneakGameToonFPS

class FactorySneakPlayer(DirectObject):
    notify = directNotify.newCategory("FactorySneakPlayer")

    SPAWN_POINT = Point3(21, 14.5, 3.73)

    def __init__(self, mg):
        DirectObject.__init__(self)
        self.actualAvatar = base.localAvatar
        self.beansCollected = 0
        self.moneyGui = None
        self.mg = mg
        self.toonFPS = FactorySneakGameToonFPS(mg)

    def startFPS(self, enableLookAround = True):
        self.toonFPS.load()
        self.toonFPS.start()
        if (enableLookAround == False):
            self.disableLookAround()
        self.toonFPS.gui.hp_meter.hide()

    def enableLookAround(self):
        self.toonFPS.firstPerson.disableMouse()

    def disableLookAround(self):
        self.toonFPS.firstPerson.enableMouse()

    def enableControls(self):
        self.toonFPS.reallyStart()

    def disableControls(self):
        self.toonFPS.end()

    def cleanupFPS(self):
        self.toonFPS.reallyEnd()
        self.toonFPS.cleanup()

    def spawn(self):
        self.actualAvatar.setPos(self.SPAWN_POINT)

    def setupInterface(self):
        self.moneyGui = MoneyGui()
        self.moneyGui.createGui()
        self.moneyGui.frame.setPos(self.moneyGui.frame.getPos() + (-0.25, 0, 0.175))

        self.updateBeansCollected()

    def cleanup(self):
        self.actualAvatar = None
        self.beansCollected = None
        self.cleanupFPS()
        if self.moneyGui:
            self.moneyGui.deleteGui()
            self.moneyGui = None
        self.mg = None

    def setBeansCollected(self, amt):
        self.beansCollected = amt
        self.updateBeansCollected()

    def getBeansCollected(self):
        return self.beansCollected

    def updateBeansCollected(self):
        self.moneyGui.update(self.beansCollected)

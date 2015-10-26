# Filename: DistributedBattleTrolley.py
# Created by:  blach (25Oct15)
#
# This is a new way to go into the future to battle -- the trolley.
# There has to be one sender trolley, and one drop-off trolley. They are connected in a way.

from panda3d.core import Point3, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import LerpPosInterval, LerpHprInterval

class DistributedBattleTrolley(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleTrolley')

    STAND_POSITIONS = [Point3(20, 9.11, 1), Point3(17.16, 9.11, 1), Point3(14.33, 9.11, 1), Point3(11.5, 9.11, 1)]
    TROLLEY_NEUTRAL_POS = Point3(15.751, 14.1588, -0.984615)
    TROLLEY_GONE_POS = Point3(50, 14.1588, -0.984615)
    TROLLEY_ARRIVING_START_POS = Point3(-20, 14.1588, -0.984615)

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedBattleTrolley', [State.State('off', self.enterOff, self.exitOff),
         State.State('arrived', self.enterArrived, self.exitArrived),
         State.State('gone', self.enterGone, self.exitGone),
         State.State('leaving', self.enterLeaving, self.exitLeaving),
         State.State('arriving', self.enterArriving, self.exitArriving)], 'off', 'off')
        self.fsm.enterInitialState()
        self.trolleyStation = None
        self.trolleyCar = None
        self.trolleyKey = None
        self.soundMoving = base.loadSfx('phase_4/audio/sfx/SZ_trolley_away.mp3')
        self.soundBell = base.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.mp3')

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterArrived(self):
        self.trolleyCar.setPos(self.TROLLEY_NEUTRAL_POS)

    def exitArrived(self):
        pass

    def enterGone(self):
        self.trolleyCar.setPos(self.TROLLEY_GONE_POS)

    def exitGone(self):
        pass

    def enterArriving(self):
        base.playSfx(self.soundMoving)
        self.moveTrack = ParallelEndTogether()

    def exitArriving(self):
        pass

    def enterLeaving(self):
        base.playSfx(self.soundMoving)
        base.playSfx(self.soundBell)

    def exitLeaving(self):
        pass

    def generate(self):
        DistributedObject.announceGenerate(self)
        self.trolleyStation = self.cr.playGame.hood.loader.geom.find('**/prop_trolley_station_DNARoot')
        self.trolleyCar = self.trolleyStation.find('**/trolley_car')
        self.trolleyKey = self.trolleyStation.find('**/key')

    def delete(self):
        self.trolleyStation = None
        self.trolleyKey = None
        self.soundMoving = None
        self.soundBell = None
        self.troleyCar = None
        DistributedObject.delete(self)

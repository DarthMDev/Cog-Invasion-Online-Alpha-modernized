# Filename: DistributedBattleTrolley.py
# Created by:  blach (25Oct15)
#
# This is a new way to go into the future to battle -- the trolley.

from panda3d.core import Point3, Vec3, TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import LerpPosInterval, LerpHprInterval, LerpQuatInterval, Parallel, Sequence, Wait, Func
from direct.gui.DirectGui import DirectButton

from lib.coginvasion.globals import CIGlobals

class DistributedBattleTrolley(DistributedObject):
    notify = directNotify.newCategory('DistributedBattleTrolley')

    STAND_POSITIONS = [Point3(-4.75, -5, 1.4), Point3(-4.75, -1.6, 1.4), Point3(-4.75, 1.6, 1.4), Point3(-4.75, 5, 1.4)]
    TROLLEY_NEUTRAL_POS = Point3(15.751, 14.1588, -0.984615)
    TROLLEY_GONE_POS = Point3(50, 14.1588, -0.984615)
    TROLLEY_ARRIVING_START_POS = Point3(-20, 14.1588, -0.984615)
    CAM_POS = Point3(-36.1269, 0.742999, 7.3503)
    CAM_HPR = Vec3(-90, -1.9966, 0)

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedBattleTrolley', [State.State('off', self.enterOff, self.exitOff),
         State.State('wait', self.enterWait, self.exitWait),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('leaving', self.enterLeaving, self.exitLeaving),
         State.State('arriving', self.enterArriving, self.exitArriving)], 'off', 'off')
        self.fsm.enterInitialState()
        self.trolleyStation = None
        self.trolleyCar = None
        self.trolleyKey = None
        self.countdownText = None
        self.soundMoving = base.loadSfx('phase_4/audio/sfx/SZ_trolley_away.mp3')
        self.soundBell = base.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.mp3')
        self.toZone = 0
        self.localAvOnTrolley = False

    def setToZone(self, zone):
        self.toZone = zone

    def getToZone(self):
        return self.toZone

    def enterOff(self, ts = 0):
        pass

    def exitOff(self):
        pass

    def enterWait(self, ts = 0):
        self.trolleyCar.setPos(self.TROLLEY_NEUTRAL_POS)

    def exitWait(self):
        pass

    def enterWaitCountdown(self, ts = 0):
        self.trolleyCar.setPos(self.TROLLEY_NEUTRAL_POS)
        if self.countdownText:
            self.countdownTrack = Sequence()
            for i in range(10):
                self.countdownTrack.append(Func(self.countdownText.node().setText, str(10 - i)))
                self.countdownTrack.append(Wait(1.0))
            self.countdownTrack.start()

    def exitWaitCountdown(self):
        if hasattr(self, 'countdownTrack'):
            self.countdownTrack.finish()
            del self.countdownTrack
        if self.countdownText:
            self.countdownText.node().setText('')
        self.disableExitButton()

    def enterArriving(self, ts = 0):
        base.playSfx(self.soundMoving)
        self.moveTrack = LerpPosInterval(self.trolleyCar, duration = 3.0, pos = self.TROLLEY_NEUTRAL_POS,
            startPos = self.TROLLEY_ARRIVING_START_POS, blendType = 'easeOut')
        self.moveTrack.start()

    def exitArriving(self):
        self.moveTrack.finish()
        del self.moveTrack

    def enterLeaving(self, ts = 0):
        base.playSfx(self.soundMoving)
        base.playSfx(self.soundBell)
        self.moveTrack = LerpPosInterval(self.trolleyCar, duration = 3.0, pos = self.TROLLEY_GONE_POS,
            startPos = self.TROLLEY_NEUTRAL_POS, blendType = 'easeIn')
        self.moveTrack.start()

    def exitLeaving(self):
        self.moveTrack.finish()
        del self.moveTrack

    def setState(self, stateName, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.fsm.request(stateName, [ts])

    def __handleTrolleyTrigger(self, entry):
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.disablePies()
        self.notify.info('Waiting for response from server to enter trolley')
        self.sendUpdate('requestBoard')
        base.localAvatar.walkControls.setCollisionsActive(0)

    def fillSlot(self, index, avId):
        toon = self.cr.doId2do.get(avId)
        toon.stopSmooth()
        if toon:
            toon.wrtReparentTo(self.trolleyCar)
            slotPos = self.STAND_POSITIONS[index]
            toon.headsUp(slotPos)
            track = Sequence(
             Func(toon.setAnimState, 'run'),
             LerpPosInterval(
              toon,
              duration = 1.0,
              pos = slotPos,
              startPos = toon.getPos()
             ),
             Func(toon.setAnimState, 'neutral'),
             Func(toon.setHpr, 90, 0, 0)
            )
            track.start()
        if avId == base.localAvatar.doId:
            self.localAvOnTrolley = True
            base.localAvatar.stopSmartCamera()
            base.camera.wrtReparentTo(self.trolleyCar)
            camTrack = Sequence(Parallel(
             LerpPosInterval(
              base.camera,
              duration = 0.5,
              pos = self.CAM_POS,
              startPos = base.camera.getPos(),
              blendType = 'easeOut'
             ),
             LerpQuatInterval(
              base.camera,
              duration = 0.5,
              hpr = self.CAM_HPR,
              startHpr = base.camera.getHpr(),
              blendType = 'easeOut'
             )
            ), Func(self.enableExitButton))
            camTrack.start()

    def enableExitButton(self):
        gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
        up = gui.find('**/InventoryButtonUp')
        down = gui.find('**/InventoryButtonDown')
        rlvr = gui.find('**/InventoryButtonRollover')
        self.exitButton = DirectButton(image = (up, down, rlvr), relief = None,
                                       text = 'Exit', text_fg = (1, 1, 0.65, 1),
                                       text_pos=(0, -0.23), text_scale = 0.8,
                                       image_scale = (11, 1, 11), pos = (0, 0, -0.8),
                                       scale = 0.15, command = self.__handleExitButton,
                                       image_color = (1, 0, 0, 1))

    def __handleExitButton(self):
        if self.fsm.getCurrentState().getName() == 'waitCountdown' and self.localAvOnTrolley == True:
            self.disableExitButton()
            self.sendUpdate('requestHopOff')

    def disableExitButton(self):
        if hasattr(self, 'exitButton'):
            self.exitButton.destroy()
            del self.exitButton

    def emptySlot(self, index, avId):
        toon = self.cr.doId2do.get(avId)
        toon.stopSmooth()
        currToonPos = toon.getPos(render)
        toon.wrtReparentTo(render)
        slotPos = self.STAND_POSITIONS[index]
        endPos = (-20, slotPos.getY(), 0.0)
        toon.setPos(self.trolleyCar, endPos)
        endPosWrtRender = toon.getPos(render)
        toon.setPos(currToonPos)
        toon.headsUp(self.trolleyCar, endPos)
        track = Sequence(
         Func(toon.setAnimState, 'run'),
         LerpPosInterval(
          toon,
          duration = 1.0,
          pos = endPosWrtRender,
          startPos = currToonPos
         ),
         Func(toon.setAnimState, 'neutral'),
         Func(toon.startSmooth)
        )
        if avId == base.localAvatar.doId:
            track.append(Func(self.__hoppedOffTrolley))
        track.start()

    def __hoppedOffTrolley(self):
        self.acceptOnce('entertrolley_sphere', self.__handleTrolleyTrigger)
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')

    def generate(self):
        DistributedObject.announceGenerate(self)
        self.trolleyStation = self.cr.playGame.hood.loader.geom.find('**/prop_trolley_station_DNARoot')
        self.trolleyCar = self.trolleyStation.find('**/trolley_car')
        self.trolleyKey = self.trolleyStation.find('**/key')
        tn = TextNode('trolleycountdowntext')
        tn.setFont(CIGlobals.getMickeyFont())
        tn.setTextColor(1, 0, 0, 1)
        self.countdownText = self.trolleyStation.attachNewNode(tn)
        self.countdownText.setScale(3.0)
        self.countdownText.setPos(14.58, 10.77, 11.17)
        self.acceptOnce('entertrolley_sphere', self.__handleTrolleyTrigger)

    def delete(self):
        self.trolleyStation = None
        self.trolleyKey = None
        self.soundMoving = None
        self.soundBell = None
        self.troleyCar = None
        self.ignore('entertrolley_sphere')
        DistributedObject.delete(self)

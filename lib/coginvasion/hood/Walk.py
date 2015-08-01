"""

  Filename: Walk.py
  Created by: blach (15Dec14)

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.StateData import StateData
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

class Walk(StateData):
    notify = directNotify.newCategory("Walk")

    def __init__(self, doneEvent):
        StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM('Walk', [
            State('off', self.enterOff, self.exitOff, ['walking', 'deadWalking']),
            State('walking', self.enterWalking, self.exitWalking),
            State('deadWalking', self.enterDeadWalking, self.exitDeadWalking)],
            'off', 'off')
        self.fsm.enterInitialState()

    def load(self):
        pass

    def unload(self):
        del self.fsm

    def enter(self):
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableAvatarControls()
        if base.localAvatar.getHealth() > 0:
            base.localAvatar.b_setAnimState("neutral")
        else:
            base.localAvatar.b_setAnimState("deadNeutral")

    def exit(self):
        self.fsm.request('off')
        base.localAvatar.disableAvatarControls()
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWalking(self):
        base.localAvatar.setWalkSpeedNormal()

    def exitWalking(slef):
        pass

    def enterDeadWalking(self):
        base.localAvatar.setWalkSpeedSlow()

    def exitDeadWalking(self):
        pass

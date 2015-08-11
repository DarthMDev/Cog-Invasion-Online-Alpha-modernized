# Filename: DistributedPieTurretAI.py
# Created by:  blach (14Jun15)
# Updated by:  DecodedLogic (10Aug15)

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.distributed.ClockDelta import globalClockDelta
from direct.task.Task import Task

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI

class DistributedPieTurretAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory('DistributedPieTurretAI')
    maximumRange = 40

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.owner = 0
        self.mgr = None

    def setManager(self, mgr):
        self.mgr = mgr

    def getManager(self):
        return self.mgr

    def setHealth(self, hp):
        DistributedAvatarAI.setHealth(self, hp)
        if hp < 1:
            self.getManager().sendUpdateToAvatarId(self.getOwner(), 'yourTurretIsDead', [])
            self.sendUpdate('die', [])
            Sequence(Wait(2.0), Func(self.getManager().killTurret, self.doId)).start()

    def startScanning(self, afterShoot = 0):
        if self.getHealth() > 0:
            timestamp = globalClockDelta.getFrameNetworkTime()
            self.sendUpdate('scan', [timestamp, afterShoot])
            base.taskMgr.add(self.__scan, self.uniqueName('DistributedPieTurretAI-scan'))

    def __scan(self, task):
        try:
            if self.getHealth() < 1:
                return Task.done
            closestSuit = None
            suitId2range = {}
            for obj in self.air.doId2do.values():
                if obj.zoneId == self.zoneId:
                    if obj.__class__.__name__ == 'DistributedSuitAI':
                        if obj.getHealth() > 0:
                            suitId2range[obj.doId] = obj.getDistance(self)
            ranges = []
            for distance in suitId2range.values():
                ranges.append(distance)
            ranges.sort()
            for suitId in suitId2range.keys():
                distance = suitId2range[suitId]
                if distance == ranges[0]:
                    if distance <= self.maximumRange:
                        closestSuit = self.air.doId2do.get(suitId)
                        break
            if closestSuit and self.getHealth() > 0:
                self.sendUpdate('shoot', [closestSuit.doId])
                Sequence(Wait(0.5), Func(self.startScanning, 1)).start()
                return Task.done
            task.delayTime = 0.5
            return Task.again
        except:
            return Task.done

    def setOwner(self, avId):
        self.owner = avId

    def d_setOwner(self, avId):
        self.sendUpdate('setOwner', [avId])

    def b_setOwner(self, avId):
        self.d_setOwner(avId)
        self.setOwner(avId)

    def getOwner(self):
        return self.owner

    def disable(self):
        base.taskMgr.remove(self.uniqueName('DistributedPieTurretAI-scan'))
        self.owner = None
        self.mgr = None
        DistributedSmoothNodeAI.disable(self)
        DistributedAvatarAI.disable(self)

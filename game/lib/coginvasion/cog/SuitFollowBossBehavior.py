"""

  Filename: SuitFollowBossBehavior.py
  Created by: DecodedLogic (02Sep15)

"""

from lib.coginvasion.cog.SuitPathBehavior import SuitPathBehavior
from lib.coginvasion.cog.SuitHabitualBehavior import SuitHabitualBehavior

from direct.task.Task import Task

class SuitFollowBossBehavior(SuitPathBehavior, SuitHabitualBehavior):
    
    LEEWAY_DISTANCE = 4
    
    def __init__(self, suit, boss):
        SuitPathBehavior.__init__(self, suit, exitOnWalkFinish = False)
        self.boss = boss
        self.followBossTaskName = self.suit.uniqueName('followBoss')
        
    def enter(self):
        SuitPathBehavior.enter(self)

        # Let's start following the boss.
        self.__updatePath()
        
        # Let's begin waiting for the suit to get in front of the boss.
        taskMgr.add(self.__followBoss, self.followBossTaskName)
        
    def exit(self):
        SuitPathBehavior.exit(self)
        taskMgr.remove(self.followBossTaskName)
        
    def unload(self):
        SuitPathBehavior.unload(self)
        del self.boss
        del self.followBossTaskName
        
    def __updatePath(self):
        # Let's handle abandoning follow, boss deletion, etc.
        if not self.boss or not self.isBossInManager() or self.shouldAbandonFollow() or hasattr(self.boss, 'DELETED'):
            self.suit.b_setAnimState('neutral')
            self.exit()
            
        if hasattr(self.boss, 'currentPath'):
            bossSpot = self.boss.getCurrentPath()
            currentPathQueue = self.suit.getCurrentPathQueue()
            
            # Let's create a path.
            if self.suit.getCurrentPath() == bossSpot:
                self.createPath(pathKey = bossSpot, fromCurPos = True)
            else:
                currentPathQueue = self.findPath(self.suit.getHood(), self.suit.getCurrentPath(), bossSpot)
                currentPathQueue.remove(currentPathQueue[0])
                self.createPath(fromCurPos = True)
            self.acceptOnce(self.walkTrack.getDoneEvent(), self.__updatePath)
        else:
            self.exit()
        
    def __followBoss(self, task):
        # Let's cancel the task if the behavior was unloaded
        # or the boss was killed.
        if not hasattr(self, 'suit') or self.boss.isEmpty() or not self.boss.isEmpty() and self.boss.isDead():
            return Task.done
        
        # We need to stop in front of the boss to protect him.
        if self.suit.getDistance(self.boss) <= self.LEEWAY_DISTANCE:
            self.suit.d_stopMoveInterval()
            if self.walkTrack:
                self.clearWalkTrack()
                self.suit.b_setAnimState('neutral')
                self.suit.setH(self.suit.getH() - 180)
                self.suit.d_setH(self.suit.getH())
                self.exit()
            return Task.done
        return Task.cont
    
    def shouldAbandonFollow(self):
        suitsByBoss = self.getSuitsByBoss()
        return float(len(suitsByBoss)) / float(self.getBackupCalledIn()) >= 0.4
    
    def getSuitsByBoss(self):
        suits = []
        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if className == 'DistributedSuitAI':
                if obj.zoneId == self.suit.zoneId:
                    if not obj.isDead() and not obj == self.boss and not obj == self.suit:
                        if obj.getDistance(self.boss) <= (self.LEEWAY_DISTANCE * 3):
                            suits.append(obj)
        return suits
    
    def getBackupCalledIn(self):
        from lib.coginvasion.cog.SuitCallInBackupBehavior import SuitCallInBackupBehavior
        behaviorClass = SuitCallInBackupBehavior
        if hasattr(self.boss, 'DELETED') or not self.boss.getBrain():
            return 0
        behavior = self.boss.getBrain().getBehavior(behaviorClass)
        return behavior.getCalledInBackup()
    
    def isBossInManager(self):
        return self.boss in self.suit.getManager().suits.values()
            
    def shouldStart(self):
        if self.boss and not self.boss.isDead() and self.isBossInManager() and self.suit.getDistance(self.boss) > self.LEEWAY_DISTANCE:
            return True
        return False
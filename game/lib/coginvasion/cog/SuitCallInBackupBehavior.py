"""

  Filename: SuitCallInBackupBehavior.py
  Created by: DecodedLogic (14Sep15)

"""

from lib.coginvasion.cog.SuitHabitualBehavior import SuitHabitualBehavior
from lib.coginvasion.cog.SuitFollowBossBehavior import SuitFollowBossBehavior
from lib.coginvasion.cog.SuitHealBossBehavior import SuitHealBossBehavior
from lib.coginvasion.cog import Variant

from direct.task.Task import Task
from direct.interval.IntervalGlobal import Sequence, Wait, Func
import random

class SuitCallInBackupBehavior(SuitHabitualBehavior):
    
    def __init__(self, suit):
        doneEvent = 'suit%s-callInBackup'
        SuitHabitualBehavior.__init__(self, suit, doneEvent)
        self.backup_levels = {1: range(1, 4 + 1),
                        2: range(5, 8 + 1),
                        3: range(9, 12 + 1)}
        self.backupLevel = -1
        self.backupAvailable = True
        self.backupCooldown = None
        self.calledInBackup = 0
        
    def enter(self):
        SuitHabitualBehavior.enter(self)
        self.__toggleBackupAvailable()
        self.backupLevel += 1
        backupCooldown = random.randint(16, 20)
        self.backupCooldown = Sequence(Wait(backupCooldown), Func(self.__toggleBackupAvailable))
        taskMgr.doMethodLater(6, self.__spawnBackupGroup, self.suit.uniqueName('Spawn Backup Group'))
        self.suit.getManager().sendSysMessage('%s is calling in backup!' % (self.suit.getName()))
        self.exit()
        
    def unload(self):
        SuitHabitualBehavior.unload(self)
        if self.backupCooldown:
            self.backupCooldown.pause()
            self.backupCooldown = None
        del self.backupLevel
        del self.backup_levels
        del self.backupAvailable
        
    def __toggleBackupAvailable(self):
        if self.backupAvailable:
            self.backupAvailable = False
        else:
            self.backupAvailable = True
        
    def __spawnBackupGroup(self, task):
        if not hasattr(self, 'suit') or hasattr(self.suit, 'DELETED'):
            return Task.done
        mgr = self.suit.getManager()
        if mgr.isCogCountFull() or mgr.suits == None:
            return Task.done
        requestSize = random.randint(0, 7)
        for _ in range(requestSize):
            if mgr.isCogCountFull():
                break
            newSuit = mgr.createSuit(levelRange = self.backup_levels[self.backupLevel + 1], anySuit = 1, variant = Variant.SKELETON)
            newSuit.addBehavior(SuitHealBossBehavior(newSuit, self.suit), priority = 5)
            newSuit.addBehavior(SuitFollowBossBehavior(newSuit, self.suit), priority = 4)
        self.calledInBackup += requestSize
        task.delayTime = 4
        return Task.again
    
    def getCalledInBackup(self):
        return self.calledInBackup
        
    def shouldStart(self):
        hpPerct = float(self.suit.getHealth()) / float(self.suit.getMaxHealth())
        if self.backupLevel == -1 and 0.50 <= hpPerct <= 0.75:
            return self.backupAvailable
        elif self.backupLevel == 0 and 0.25 <= hpPerct <= 0.50:
            return self.backupAvailable
        elif self.backupLevel == 1 and 0.0 <= hpPerct <= 0.25:
            return self.backupAvailable
        return False
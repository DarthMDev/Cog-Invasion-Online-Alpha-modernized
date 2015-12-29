"""

  Filename: SuitCallInBackupBehavior.py
  Created by: DecodedLogic (14Sep15)

"""

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.cog.SuitFollowBossBehavior import SuitFollowBossBehavior
from lib.coginvasion.cog.SuitHealBossBehavior import SuitHealBossBehavior
from lib.coginvasion.cog import Variant

from direct.task.Task import Task
from direct.interval.IntervalGlobal import Sequence, Wait, Func
import random

SPEECH_BY_BACKUP_LVL = {0: ['Gah! I need backup!', 'Get me some backup!', 'Get them!!!', 'Attack!!'],
                        1: ["Is that all you got, Toons?", "There's more where that came from!", "Send in higher backup!",
                            "I need stronger reinforcements!"],
                        2: ["No, no, it's not working... give me everything you got!", "I need everything I can get!",
                            "Get me the highest level of backup you have!", "Just try and get through these reinforcements!"]}

class SuitCallInBackupBehavior(SuitBehaviorBase):

    def __init__(self, suit):
        doneEvent = 'suit%s-callInBackup'
        SuitBehaviorBase.__init__(self, suit, doneEvent)
        self.backup_levels = {1: range(1, 4 + 1),
                        2: range(5, 8 + 1),
                        3: range(9, 12 + 1)}
        self.backupLevel = -1
        self.backupAvailable = True
        self.backupCooldown = None
        self.calledInBackup = 0
        self.isEntered = 0

    def enter(self):
        SuitBehaviorBase.enter(self)
        self.__toggleBackupAvailable()
        self.backupLevel += 1
        backupCooldown = random.randint(16, 20)
        self.backupCooldown = Sequence(Wait(backupCooldown), Func(self.__toggleBackupAvailable))
        taskMgr.doMethodLater(8, self.__spawnBackupGroup, self.suit.uniqueName('Spawn Backup Group'))
        self.suit.getManager().flyAwayAllSuits()
        self.suit.getManager().sendSysMessage('The {0} is calling in backup level {1}!'.format(self.suit.getName(), self.backupLevel + 1))
        self.suit.d_setChat(random.choice(SPEECH_BY_BACKUP_LVL[self.backupLevel]))
        self.exit()

    def unload(self):
        SuitBehaviorBase.unload(self)
        if self.backupCooldown:
            self.backupCooldown.pause()
            self.backupCooldown = None
        del self.backupLevel
        del self.backup_levels
        del self.backupAvailable

    def __toggleBackupAvailable(self):
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
            #newSuit.addBehavior(SuitHealBossBehavior(newSuit, self.suit), priority = 5)
            newSuit.addBehavior(SuitFollowBossBehavior(newSuit, self.suit), priority = 4)
        self.calledInBackup += requestSize
        task.delayTime = 4
        return Task.again

    def getCalledInBackup(self):
        return self.calledInBackup

    def shouldStart(self):
        hpPerct = float(self.suit.getHealth()) / float(self.suit.getMaxHealth())
        if self.backupLevel == -1 and 0.7 <= hpPerct <= 0.8:
            return self.backupAvailable
        elif self.backupLevel == 0 and 0.4 <= hpPerct <= 0.7:
            return self.backupAvailable
        elif self.backupLevel == 1 and 0.0 <= hpPerct <= 0.4:
            return self.backupAvailable
        return False

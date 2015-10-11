"""

  Filename: SuitAttackBehavior.py
  Created by: DecodedLogic (13Sep15)

"""

from lib.coginvasion.cog.SuitHabitualBehavior import SuitHabitualBehavior
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit import SuitAttacks

from direct.distributed.ClockDelta import globalClockDelta
from direct.task.Task import Task
import random, operator

class SuitAttackBehavior(SuitHabitualBehavior):

    ATTACK_DISTANCE = 40.0
    ATTACK_COOLDOWN = 10
    MAX_ATTACKERS = 3
    ABANDON_ATTACK_PERCT = 0.18

    def __init__(self, suit):
        SuitHabitualBehavior.__init__(self, suit, doneEvent = 'suit%s-attackDone' % suit.doId)
        self.avatarsInRange = []
        self.maxAttacksPerSession = 3
        self.attacksThisSession = 0
        self.attacksDone = 0
        self.target = None
        self.canAttack = True
        self.origHealth = None

        level = self.suit.getLevel()
        if 1 <= level <= 5:
            self.maxAttacksPerSession = 3
        elif 5 <= level <= 10:
            self.maxAttacksPerSession = 4
        elif 9 <= level <= 12:
            self.maxAttacksPerSession = 5

    def enter(self):
        SuitHabitualBehavior.enter(self)
        self.origHealth = self.suit.getHealth()
        self.attacksThisSession = 0
        self.startAttacking()

    def exit(self):
        SuitHabitualBehavior.exit(self)

    def unload(self):
        SuitHabitualBehavior.exit(self)
        self.avatarsInRange = None
        self.origHealth = None
        del self.origHealth
        del self.avatarsInRange
        del self.maxAttacksPerSession
        del self.attacksThisSession
        del self.attacksDone
        del self.target
        del self.canAttack

    def startAttacking(self, task = None):
        if hasattr(self.suit, 'DELETED') or not hasattr(self, 'attacksThisSession'):
            self.stopAttacking()
            if task:
                return Task.done
        # Do we need to reset the avatars in-range?
        if self.attacksThisSession > 0:
            self.resetAvatarsInRange()

        # Stop attacking if low on health or if there's nothing around to attack.
        if hasattr(self.suit, 'DELETED'):
            self.stopAttacking()
            return

        # Let's check our panic behavior.
        from lib.coginvasion.cog.SuitPanicBehavior import SuitPanicBehavior
        brain = self.suit.getBrain()
        panicBehavior = brain.getBehavior(SuitPanicBehavior)
        healthPerct = float(self.suit.getHealth()) / float(self.suit.getMaxHealth())
        origHealthPerct = float(self.origHealth) / float(self.suit.getMaxHealth())

        if len(self.avatarsInRange) < 1 or panicBehavior and healthPerct <= panicBehavior.getPanicHealthPercentage() or healthPerct - origHealthPerct >= self.ABANDON_ATTACK_PERCT:
            self.stopAttacking()
            return

        # Let's select a target and look at them.
        target = self.avatarsInRange[0]
        self.suit.b_setAnimState('neutral')
        self.suit.headsUp(target)

        # Choose a random attack and start it.
        attack = random.choice(self.suit.suitPlan.getAttacks())
        attackIndex = SuitAttacks.SuitAttackLengths.keys().index(attack)
        attackTaunt = random.randint(0, len(CIGlobals.SuitAttackTaunts[attack]) - 1)
        timestamp = globalClockDelta.getFrameNetworkTime()
        if self.suit.isDead():
            self.stopAttacking()
            return
        self.suit.sendUpdate('doAttack', [attackIndex, target.doId, timestamp])
        self.suit.d_setChat(CIGlobals.SuitAttackTaunts[attack][attackTaunt])
        self.attacksThisSession += 1
        self.attacksDone += 1

        # Let's setup the attack cooldown.
        #if target.__class__.__name__ == 'DistributedToonAI':
        #    self.ATTACK_COOLDOWN = random.randint(6, 12)
        #else:
        #    self.ATTACK_COOLDOWN = random.randint(2, 6)
        self.ATTACK_COOLDOWN = SuitAttacks.SuitAttackLengths[attack]

        # Are we allowed to continue attacking?
        if self.attacksThisSession < self.maxAttacksPerSession:
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.startAttacking, self.suit.uniqueName('attackTask'))
        else:
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.stopAttacking, self.suit.uniqueName('finalAttack'))

        if task:
            return Task.done

    def __doAttackCooldown(self, task):
        self.canAttack = True

    def stopAttacking(self, task = None):
        if hasattr(self, 'suit'):
            self.canAttack = False
            self.origHealth = self.suit.getHealth()
            self.attacksThisSession = 0
            self.avatarsInRange = []
            self.ATTACK_COOLDOWN = random.randint(8, 20)
            taskMgr.doMethodLater(self.ATTACK_COOLDOWN, self.__doAttackCooldown, self.suit.uniqueName('Attack Cooldown'))
        self.exit()
        if task:
            return Task.done

    def resetAvatarsInRange(self):
        toonObjsInRange = {}
        self.avatarsInRange = []

        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if className in ['DistributedToonAI', 'DistributedPieTurretAI']:
                if obj.zoneId == self.suit.zoneId:
                    if not obj.isDead():
                        dist = obj.getDistance(self.suit)
                        if className == 'DistributedToonAI' and obj.getNumAttackers() >= self.MAX_ATTACKERS or className == 'DistributedToonAI' and obj.getGhost():
                            continue
                        if dist <= self.ATTACK_DISTANCE:
                            toonObjsInRange.update({obj : dist})

        toonObjsInRange = sorted(toonObjsInRange.items(), key = operator.itemgetter(1))
        for toonObj, _ in toonObjsInRange:
            self.avatarsInRange.append(toonObj)

    def shouldStart(self):
        self.resetAvatarsInRange()

        if len(self.avatarsInRange) > 0 and self.canAttack:
            return True
        return False

    def getTarget(self):
        return self.target

    def getAttacksDone(self):
        return self.attacksDone

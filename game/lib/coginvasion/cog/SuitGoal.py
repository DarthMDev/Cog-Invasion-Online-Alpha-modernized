# Filename: SuitGoal.py
# Created by:  blach (26Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.FSM import FSM

from SuitAttackBehaviorAI import SuitAttackBehaviorAI
from SuitPursueToonBehaviorAI import SuitPursueToonBehaviorAI

class SuitGoal(FSM):
    notify = directNotify.newCategory('SuitGoal')
    
    def __init__(self, brain):
        FSM.__init__(self, 'SuitGoal')
        self.brain = brain
        self.air = self.brain.suit.air
        self.suit = self.brain.suit
        
    def cleanup(self):
        self.brain = None
        self.air = None
        self.suit = None
        FSM.cleanup(self)
        
class KillToonGoal(SuitGoal):
    notify = directNotify.newCategory('KillToonGoal')
    
    # ----- Behaviors/states -----
    # Pursue toon
    # Attack toon
    
    TOO_FAR_TO_DECIDE = 50.0
                 
    def __init__(self, brain):
        SuitGoal.__init__(self, brain)
        self.target = None
        self.battle = self.suit.getManager().getBattle()
        
    def enterAttack(self):
        self.behavior = SuitAttackBehaviorAI(self.suit, self.target, self.suit.uniqueName('attackToonDone'))
        self.behavior.load()
        self.behavior.enter()
        
    def exitAttack(self):
        self.behavior.exit()
        self.behavior.unload()
        del self.behavior
        
    def enterPursueToon(self):
        self.behavior = SuitPursueToonBehaviorAI(self.suit, self.target, self.suit.uniqueName('pursueToonDone'))
        self.behavior.load()
        self.behavior.enter()
        
    def exitPursueToon(self):
        self.behavior.exit()
        self.behavior.unload()
        del self.behavior
        
    def getAvIdsSortedByDistance(self):
        avIds = list(self.battle.avIds)
        avIds.sort(key = lambda avId: self.air.doId2do.get(avId).getDistance(self.suit))
        return avIds
        
    def _sortAvIdsByNumTargeters(self, avIds):
        avIds.sort(key = lambda avId: len(self.battle.avId2suitsTargeting[avId]))
        return avIds
        
    def pickNewTarget(self):
        avIds = self.getAvIdsSortedByDistance()
        if self.air.do2Id2do.get(avIds[0]).getDistance(self.suit) >= self.TOO_FAR_TO_DECIDE:
            # Let me just pick the toon with the least amount of targeters because all the
            # toons are too far away to decide who's closest.
            avIds = self._sortAvIdsByNumTargeters(avIds)
            # This is now the toon with the least number of attackers.
            choice = avIds[0]
            self.target = choice
        else:
            # I can tell exactly who is closest to me. Target them!
            choice = avIds[0]
            self.target = choice
            
    def cleanup(self):
        self.target = None
        self.battle = None
        SuitGoal.cleanup(self)
        

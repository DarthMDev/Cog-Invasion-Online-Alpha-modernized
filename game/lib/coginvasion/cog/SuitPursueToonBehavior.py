# Filename: SuitPursueToonBehavior.py
# Created by:  blach (29Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State

from SuitPathBehavior import SuitPathBehavior
import SuitUtils
import SuitAttacks

import random

class SuitPursueToonBehavior(SuitPathBehavior):
    notify = directNotify.newCategory('SuitPursueToonBehavior')
    
    RemakePathDistance = 20.0
    
    def __init__(self, suit, pathFinder):
        SuitPathBehavior.__init__(self, suit, False)
        self.fsm = ClassicFSM.ClassicFSM('SuitPursueToonBehavior', [State.State('off', self.enterOff, self.exitOff),
         State.State('pursue', self.enterPursue, self.exitPursue),
         State.State('attack', self.enterAttack, self.exitAttack)], 'off', 'off')
        self.fsm.enterInitialState()
        self.air = self.suit.air
        self.target = None
        self.targetId = None
        self.pathFinder = pathFinder
        
    def enter(self):
        print 'enter SuitPursueToonBehavior'
        SuitPathBehavior.enter(self)
        # Choose the toon that is the closest to this suit as the target.
        avIds = list(self.battle.avIds)
        avIds.sort(key = lambda avId: self.air.doId2do.get(avId).getDistance(self.suit))
        self.targetId = avIds[0]
        self.target = self.air.doId2do.get(self.targetId)
        # Choose a distance that is good enough to attack this target.
        self.attackSafeDistance = random.uniform(5.0, 19.0)
        # Now, chase them down!
        self.fsm.request('pursue')
        
    def exit(self):
        print 'exit SuitPursueToonBehavior'
        self.target = None
        self.targetId = None
        self.fsm.request('off')
        SuitPathBehavior.exit(self)
        
    def unload(self):
        self.mgr = None
        self.battle = None
        self.target = None
        self.targetId = None
        self.air = None
        SuitPathBehavior.unload(self)
    
    def enterOff(self):
        pass
        
    def exitOff(self):
        pass
        
    def enterAttack(self):
        taskMgr.add(self._attackTask, self.suit.uniqueName('attackToonTask'))
        
    def _attackTask(self, task):
        if self.suit.getDistance(self.target) > self.attackSafeDistance:
            # Nope, we're too far away! We need to chase them down!
            self.fsm.request('pursue')
            return task.done
        attack = SuitUtils.attack(self.suit, self.target)
        timeout = SuitAttacks.SuitAttackLengths[attack]
        task.delayTime = timeout
        return task.again
        
    def exitAttack(self):
        taskMgr.remove(self.suit.uniqueName('attackToonTask'))
        
    def enterPursue(self):
        # Make our initial path to the toon.
        print 'enter pursue'
        self.lastCheckedPos = self.target.getPos(render)
        self.createPath(self.target)
        taskMgr.add(self._pursueTask, self.suit.uniqueName('pursueToonTask'))
        
    def _pursueTask(self, task):
        print 'pursue task'
        currPos = self.target.getPos(render)
        if self.suit.getDistance(self.target) <= self.attackSafeDistance:
            print 'safe to attack'
            # We're a good distance to attack this toon. Let's do it.
            self.fsm.request('attack')
            return task.done
        elif (currPos.getXy() - self.lastCheckedPos.getXy()).length() >= SuitPursueToonBehavior.RemakePathDistance:
            print 'new path'
            # They're too far from where we're trying to go! Make a new path to where they are!
            self.lastCheckedPos = self.target.getPos(render)
            self.createPath(self.target)
        task.delayTime = 1.0
        return task.again
        
    def exitPursue(self):
        print 'exit pursue'
        taskMgr.remove(self.suit.uniqueName('pursueToonTask'))
        del self.lastCheckedPos
        self.clearWalkTrack()
        
    def shouldStart(self):
        return True

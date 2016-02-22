########################################
# Filename: SuitBehaviorBase.py
# Created by: DecodedLogic (02Sep15)
########################################

from direct.showbase.DirectObject import DirectObject

class SuitBehaviorBase(DirectObject):
    
    def __init__(self, suit, doneEvent = None):
        if doneEvent == None:
            doneEvent = 'suit%s-behaviorDone' % (suit.doId)
        self.doneEvent = doneEvent
        self.suit = suit
        
    def enter(self):
        if self.isEntered:
            return
        self.isEntered = 1
        
    def exit(self):
        if self.isEntered:
            self.isEntered = 0
            messenger.send(self.doneEvent)
            
    def canEnter(self):
        return not self.isEntered
    
    def load(self):
        pass
    
    def unload(self):
        if hasattr(self, 'suit'):
            self.suit = None
            del self.suit
        del self.isEntered
        del self.doneEvent
        
    def shouldStart(self):
        pass
    
    def isActive(self):
        return self.isEntered
    
    def getDoneEvent(self):
        return self.doneEvent
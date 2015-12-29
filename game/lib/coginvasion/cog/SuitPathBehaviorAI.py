# Filename: SuitPathBehaviorAI.py
# Created by:  blach (28Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.StateData import StateData

class SuitPathBehaviorAI(StateData):
    notify = directNotify.newCategory('SuitPathBehaviorAI')
    
    def __init__(self, suit, doneEvent):
        StateData.__init__(self, doneEvent)
        self.suit = suit

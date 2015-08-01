"""

  Filename: DistributedDroppableCollectableObjectAI.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedDroppableCollectableObjectAI(DistributedNodeAI):
    notify = directNotify.newCategory("DistributedDroppableCollectableObjectAI")

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.suitMgr = None

    def setSuitManager(self, mgr):
        self.suitMgr = mgr

    def getSuitManager(self):
        return self.suitMgr

    def collectedObject(self):
        self.requestDelete()

    def delete(self):
        if self.getSuitManager():
            if self.getSuitManager().getDrops():
                self.getSuitManager().getDrops().remove(self)
        self.suitMgr = None
        DistributedNodeAI.delete(self)

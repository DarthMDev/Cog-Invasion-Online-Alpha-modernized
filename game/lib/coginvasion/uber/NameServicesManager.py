########################################
# Filename: NameServicesManager.py
# Created by: DecodedLogic (21Feb16)
########################################
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify

class NameServicesManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('NameServicesManager')
    
    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        return
    
    def d_requestName(self, name):
        self.sendUpdate('requestName', [name])
        print "Requesting name, %s." % name
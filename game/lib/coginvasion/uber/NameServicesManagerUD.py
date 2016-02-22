########################################
# Filename: NameServicesManagerUD.py
# Created by: DecodedLogic (21Feb16)
########################################
from direct.distributed.DistributedObjectUD import DistributedObjectUD
import datetime

class NameServicesManagerUD(DistributedObjectUD):
    
    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)
        self.pendingNames = []
        
    def requestName(self, name):
        accountId = self.air.getAccountIdFromSender()
        print "The name %s has been requested. Account Id: %s" % (name, accountId)
        now = datetime.datetime.now()
        date = "%s %s %s" % (now.month, now.day, now.year)
        self.pendingNames.append({'name' : name, 'accountId' : '000000', 'date' : date})
    
    def announceGenerate(self):
        DistributedObjectUD.announceGenerate(self)
        print "Hello, it's me! The NameServicesManager!"
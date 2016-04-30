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
        self.requestedNames = []
        self.requestCompleteEventName = 'NameServicesManager-RequestComplete'
        return
    
    def d_requestName(self, name):
        self.sendUpdate('requestName', [name])
    
    def d_requestNameData(self):
        self.sendUpdate('requestNameData', [])
        print 'Requesting Data...'
        
    def nameDataRequest(self, names, avatarIds, dates, statuses):
        print 'Got a reply.'
        for i in xrange(len(names)):
            request = dict()
            request['name'] = str(names[i])
            request['avId'] = int(avatarIds[i])
            request['date'] = str(dates[i])
            request['status'] = int(statuses[i])
            self.requestedNames.append(request)
        messenger.send(self.requestCompleteEventName)
            
    def getNameRequests(self):
        return self.requestedNames
    
    def getRequestCompleteName(self):
        return self.requestCompleteEventName

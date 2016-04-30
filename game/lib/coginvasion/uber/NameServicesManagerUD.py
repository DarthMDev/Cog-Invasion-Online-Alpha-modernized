########################################
# Filename: NameServicesManagerUD.py
# Created by: DecodedLogic (21Feb16)
########################################
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
import datetime
import json

NAME_PENDING = 0
NAME_ACCEPTED = 1
NAME_DECLINED = 2

class NameServicesManagerUD(DistributedObjectGlobalUD):
    
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.requestedNames = []
        self.dataPath = 'astron/nameRequests.json'
        
    def requestName(self, name):
        avId = self.air.getAvatarIdFromSender()
        print "The name %s has been requested. Account Id: %s" % (name, avId)
        now = datetime.datetime.now()
        date = "%s %s %s" % (now.month, now.day, now.year)
        self.requestedNames.append({'name' : name, 'avId' : str(avId), 'date' : date, 'status' : NAME_PENDING})
        self.saveData()
        
    def requestNameData(self):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if True:
            names, avatarIds, dates, statuses = [], [], [], []
            for i in xrange((len(self.requestedNames))):
                nameRequest = self.requestedNames[i]
                names.append(nameRequest['name'])
                avatarIds.append(int(nameRequest['avId']))
                dates.append(nameRequest['date'])
                statuses.append(int(nameRequest['status']))
            self.sendUpdateToAvatarId(avId, 'nameDataRequest', [names, avatarIds, dates, statuses])
        else:
            avatar.ejectSelf('Attempted to access administrator only system.')
        
    def saveData(self):
        with open(self.dataPath, 'w') as dataFile:
            json.dump(self.requestedNames, dataFile)
            
    def loadData(self):
        with open(self.dataPath, 'r') as dataFile:
            self.requestedNames = list(json.load(dataFile))
    
    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.loadData()
        
        for i in xrange(len(self.requestedNames)):
            nameRequest = self.requestedNames[i]
            print 'Name %s, was requested on %s, by %s. Status: %s' % (nameRequest['name'], nameRequest['date'], nameRequest['avId'], nameRequest['status'])
            
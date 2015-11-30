"""

  Filename: HolidayManagerUD.py
  Created by: DecodedLogic (13Nov15)

"""

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

class HolidayManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('HolidayManagerUD')
    
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        
    def setHoliday(self, holiday):
        self.holiday = holiday
        
    def requestHoliday(self):
        sender = self.air.getAccountIdFromSender()
        self.sendUpdateToAccountId(sender, 'setHoliday', [self.holiday])
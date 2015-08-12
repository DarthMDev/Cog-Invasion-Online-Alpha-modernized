# Filename: DistributedTailorNPCToon.py
# Created by:  DecodedLogic (11Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
import DistributedNPCToon

class DistributedTailorNPCToon(DistributedNPCToon.DistributedNPCToon):
    notify = directNotify.newCategory('DistributedTailorToon')
    
    def __init__(self, cr):
        DistributedNPCToon.DistributedNPCToon.__init__(self, cr)
# Filename: DistributedTailorInterior.py
# Created by: DecodedLogic (11Aug15)

from . import DistributedToonInterior

class DistributedTailorInterior(DistributedToonInterior.DistributedToonInterior):
    
    def makeInterior(self, roomIndex=None):
        DistributedToonInterior.DistributedToonInterior.makeInterior(self, roomIndex=0)
        
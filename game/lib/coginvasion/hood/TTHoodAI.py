"""

  Filename: TTHoodAI.py
  Created by: blach (20Dec14)

"""

import ToonHoodAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals

# Leave this import here until I can finish this.
#from lib.coginvasion.holiday.DistributedWinterCoachActivityAI import DistributedWinterCoachActivityAI

class TTHoodAI(ToonHoodAI.ToonHoodAI):
    notify = directNotify.newCategory("TTHoodAI")
    notify.setInfo(True)

    def __init__(self, air):
        ToonHoodAI.ToonHoodAI.__init__(self, air, CIGlobals.ToontownCentralId,
                    CIGlobals.ToontownCentral)
        self.startup()

    def startup(self):
        self.notify.info("Creating hood %s" % CIGlobals.ToontownCentral)
        self.dnaFiles = ['phase_5/dna/toontown_central_2100.pdna', 'phase_5/dna/toontown_central_2200.pdna',
            'phase_5/dna/toontown_central_2300.pdna', 'phase_4/dna/new_ttc_sz.pdna']
        ToonHoodAI.ToonHoodAI.startup(self)
        
        # This activity isn't done yet.
        #self.winterActivity = DistributedWinterCoachActivityAI(self.air)
        #self.winterActivity.generateWithRequired(self.zoneId)
        #self.winterActivity.b_setPosHpr(-41.977, -19.6017, 0.00861831, -55.4674, 0, 0)
        self.notify.info("Finished creating hood %s" % CIGlobals.ToontownCentral)

    def shutdown(self):
        self.notify.info("Shutting down hood %s" % CIGlobals.ToontownCentral)
        ToonHoodAI.ToonHoodAI.shutdown(self)
        self.winterActivity.delete()
        self.notify.info("Finished shutting down hood %s" % CIGlobals.ToontownCentral)

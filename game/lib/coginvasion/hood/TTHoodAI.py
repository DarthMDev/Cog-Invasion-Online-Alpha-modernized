"""

  Filename: TTHoodAI.py
  Created by: blach (20Dec14)

"""

import ToonHoodAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals

from lib.coginvasion.cogtropolis import DistributedCityCartAI

class TTHoodAI(ToonHoodAI.ToonHoodAI):
    notify = directNotify.newCategory("TTHoodAI")
    notify.setInfo(True)

    def __init__(self, air):
        ToonHoodAI.ToonHoodAI.__init__(self, air, CIGlobals.ToontownCentralId,
                    CIGlobals.ToontownCentral)
        self.startup()

    def startup(self):
        self.notify.info("Creating hood %s" % CIGlobals.ToontownCentral)
        self.dnaFiles = ['phase_5/dna/toontown_central_2100.dna', 'phase_5/dna/toontown_central_2200.dna',
            'phase_5/dna/toontown_central_2300.dna', 'phase_4/dna/new_ttc_sz.dna']
        ToonHoodAI.ToonHoodAI.startup(self)
        self.notify.info("Finished creating hood %s" % CIGlobals.ToontownCentral)

    def shutdown(self):
        self.notify.info("Shutting down hood %s" % CIGlobals.ToontownCentral)
        ToonHoodAI.ToonHoodAI.shutdown(self)
        self.notify.info("Finished shutting down hood %s" % CIGlobals.ToontownCentral)

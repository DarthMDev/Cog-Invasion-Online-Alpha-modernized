# Filename: OToontown.py
# Created by:  blach (12Dec15)

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import TTHood
from lib.coginvasion.hood import MGHood
from lib.coginvasion.hood import BRHood
from lib.coginvasion.hood import DLHood
from lib.coginvasion.hood import MLHood
from lib.coginvasion.hood import DGHood
from lib.coginvasion.hood import DDHood
from World import World

class OToontown(World):
    notify = directNotify.newCategory('OToontown')
    Hood2HoodClass = {CIGlobals.ToontownCentral: TTHood.TTHood,
                CIGlobals.MinigameArea: MGHood.MGHood,
                CIGlobals.TheBrrrgh: BRHood.BRHood,
                CIGlobals.DonaldsDreamland: DLHood.DLHood,
                CIGlobals.MinniesMelodyland: MLHood.MLHood,
                CIGlobals.DaisyGardens: DGHood.DGHood,
                CIGlobals.DonaldsDock: DDHood.DDHood}
    Hood2HoodState = {CIGlobals.ToontownCentral: 'TTHood',
                CIGlobals.MinigameArea: 'MGHood',
                CIGlobals.TheBrrrgh: 'BRHood',
                CIGlobals.DonaldsDreamland: 'DLHood',
                CIGlobals.MinniesMelodyland: 'MLHood',
                CIGlobals.DaisyGardens: 'DGHood',
                CIGlobals.DonaldsDock: 'DDHood'}

    def __init__(self, parentFSM, doneEvent):
        World.__init__(self, doneEvent)
        self.fsm.setName(CIGlobals.OToontown)
        self.fsm.addState(State('MGHood', self.enterMGHood, self.exitMGHood, ['quietZone']))
        self.fsm.getStateNamed('quietZone').addTransition('MGHood')
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed(CIGlobals.OToontown).addChild(self.fsm)

    def enterDDHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDDHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DonaldsDock

    def enterDGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DaisyGardens

    def enterMLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.MinniesMelodyland

    def enterDLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.DonaldsDreamland

    def enterBRHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitBRHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.TheBrrrgh

    def enterTTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitTTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.ToontownCentral

    def enterMGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        base.cr.playGame.hood = None
        self.lastHood = CIGlobals.MinigameArea

    def handleHoodDone(self):
        print 'hood done'
        doneStatus = self.hood.getDoneStatus()
        if doneStatus['zoneId'] == None or doneStatus['world'] != CIGlobals.OToontown:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.fsm.request('quietZone', [doneStatus])

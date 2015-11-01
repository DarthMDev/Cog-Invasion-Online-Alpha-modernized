"""

  Filename: PlayGame.py
  Created by: blach (28Nov14)

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.distributed.CogInvasionMsgTypes import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.hood import ZoneUtil
from panda3d.core import *

from lib.coginvasion.hood import TTHood
from lib.coginvasion.hood import MGHood
from lib.coginvasion.hood import RecoverHood
from lib.coginvasion.hood import BRHood
from lib.coginvasion.hood import DLHood
from lib.coginvasion.hood import MLHood
from lib.coginvasion.hood import DGHood
from lib.coginvasion.hood import DDHood
from lib.coginvasion.hood import CTCHood
from lib.coginvasion.cogtropolis import CTHood

from lib.coginvasion.hood.QuietZoneState import QuietZoneState
from lib.coginvasion.dna.DNAParser import *

class PlayGame(StateData):
    notify = directNotify.newCategory('PlayGame')
    Hood2HoodClass = {CIGlobals.ToontownCentral: TTHood.TTHood,
                CIGlobals.MinigameArea: MGHood.MGHood,
                CIGlobals.RecoverArea: RecoverHood.RecoverHood,
                CIGlobals.TheBrrrgh: BRHood.BRHood,
                CIGlobals.DonaldsDreamland: DLHood.DLHood,
                CIGlobals.MinniesMelodyland: MLHood.MLHood,
                CIGlobals.DaisyGardens: DGHood.DGHood,
                CIGlobals.DonaldsDock: DDHood.DDHood,
                CIGlobals.CogTropolis: CTHood.CTHood,
                CIGlobals.BattleTTC: CTCHood.CTCHood}
    Hood2HoodState = {CIGlobals.ToontownCentral: 'TTHood',
                CIGlobals.MinigameArea: 'MGHood',
                CIGlobals.RecoverArea: 'RecoverHood',
                CIGlobals.TheBrrrgh: 'BRHood',
                CIGlobals.DonaldsDreamland: 'DLHood',
                CIGlobals.MinniesMelodyland: 'MLHood',
                CIGlobals.DaisyGardens: 'DGHood',
                CIGlobals.DonaldsDock: 'DDHood',
                CIGlobals.CogTropolis: 'CTHood',
                CIGlobals.BattleTTC: 'CTCHood'}

    def __init__(self, parentFSM, doneEvent):
        StateData.__init__(self, "playGameDone")
        self.doneEvent = doneEvent
        self.fsm = ClassicFSM('PlayGame', [State('off', self.enterOff, self.exitOff, ['quietZone']),
                State('quietZone', self.enterQuietZone, self.exitQuietZone, ['TTHood', 'MGHood', 'RecoverHood',
                    'BRHood', 'DLHood', 'MLHood', 'DGHood', 'DDHood', 'CTHood', 'CTCHood']),
                State('TTHood', self.enterTTHood, self.exitTTHood, ['quietZone']),
                State('MGHood', self.enterMGHood, self.exitMGHood, ['quietZone']),
                State('RecoverHood', self.enterRecoverHood, self.exitRecoverHood, ['quietZone']),
                State('BRHood', self.enterBRHood, self.exitBRHood, ['quietZone']),
                State('DLHood', self.enterDLHood, self.exitDLHood, ['quietZone']),
                State('MLHood', self.enterMLHood, self.exitMLHood, ['quietZone']),
                State('DGHood', self.enterDGHood, self.exitDGHood, ['quietZone']),
                State('DDHood', self.enterDDHood, self.exitDDHood, ['quietZone']),
                State('CTHood', self.enterCTHood, self.exitCTHood, ['quietZone']),
                State('CTCHood', self.enterCTCHood, self.exitCTCHood, ['quietZone'])],
                'off', 'off')
        self.fsm.enterInitialState()
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('playGame').addChild(self.fsm)
        self.hoodDoneEvent = 'hoodDone'
        self.hood = None
        self.quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.quietZoneStateData = None
        self.place = None
        self.suitManager = None
        self.lastHood = None

    def enter(self, hoodId, zoneId, avId):
        StateData.enter(self)
        whereName = ZoneUtil.getWhereName(zoneId)
        loaderName = ZoneUtil.getLoaderName(zoneId)
        self.fsm.request('quietZone', [{'zoneId': zoneId,
            'hoodId': hoodId,
            'where': whereName,
            'how': 'teleportIn',
            'avId': avId,
            'shardId': None,
            'loader': loaderName}])

    def exit(self):
        StateData.exit(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterCTCHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitCTCHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.ToontownCentral

    def enterCTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitCTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.CogTropolis

    def enterDDHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDDHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.DonaldsDock

    def enterDGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.DaisyGardens

    def enterMLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.MinniesMelodyland

    def enterDLHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitDLHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.DonaldsDreamland

    def enterBRHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitBRHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.TheBrrrgh

    def enterTTHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitTTHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.ToontownCentral

    def enterMGHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitMGHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        self.lastHood = CIGlobals.MinigameArea

    def enterRecoverHood(self, requestStatus):
        self.accept(self.hoodDoneEvent, self.handleHoodDone)
        self.hood.enter(requestStatus)

    def exitRecoverHood(self):
        self.ignore(self.hoodDoneEvent)
        self.hood.exit()
        self.hood.unload()
        self.hood = None

    def setPlace(self, place):
        self.place = place

    def getPlace(self):
        return self.place

    def loadDNAStore(self):
        if hasattr(self, 'dnaStore'):
            self.dnaStore.resetAll()
            del self.dnaStore

        self.dnaStore = DNAStorage()
        loadDNAFile(self.dnaStore, 'phase_4/dna/storage.dna')
        self.dnaStore.storeFont('humanist', CIGlobals.getToonFont())
        self.dnaStore.storeFont('mickey', CIGlobals.getMickeyFont())
        self.dnaStore.storeFont('suit', CIGlobals.getSuitFont())
        loadDNAFile(self.dnaStore, 'phase_3.5/dna/storage_interior.dna')

    def enterQuietZone(self, requestStatus):
        self.acceptOnce(self.quietZoneDoneEvent, self.handleQuietZoneDone, [requestStatus])
        self.acceptOnce('enteredQuietZone', self.handleEnteredQuietZone, [requestStatus])
        self.quietZoneStateData = QuietZoneState(self.quietZoneDoneEvent, 0)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def handleEnteredQuietZone(self, requestStatus):
        hoodId = requestStatus['hoodId']
        hoodClass = self.Hood2HoodClass[hoodId]
        base.transitions.noTransitions()
        loader.beginBulkLoad('hood', hoodId, 100)
        self.loadDNAStore()
        self.hood = hoodClass(self.fsm, self.hoodDoneEvent, self.dnaStore, hoodId)
        self.hood.load()

        hoodId = requestStatus['hoodId']
        hoodState = self.Hood2HoodState[hoodId]
        self.fsm.request(hoodState, [requestStatus], exitCurrent = 0)
        self.quietZoneStateData.fsm.request('waitForSetZoneResponse')

    def handleQuietZoneDone(self, requestStatus):
        self.hood.enterTheLoader(requestStatus)
        self.hood.loader.enterThePlace(requestStatus)
        loader.endBulkLoad('hood')
        self.exitQuietZone()

    def handleHoodDone(self):
        doneStatus = self.hood.getDoneStatus()
        if doneStatus['zoneId'] == None:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.fsm.request('quietZone', [doneStatus])

    def exitQuietZone(self):
        self.ignore('enteredQuietZone')
        self.ignore(self.quietZoneDoneEvent)
        self.quietZoneStateData.exit()
        self.quietZoneStateData.unload()
        self.quietZoneStateData = None

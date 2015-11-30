# Filename: DistributedSuitManagerAI.py
# Created by:  blach (22Dec14)

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from lib.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from lib.coginvasion.cog import Variant
from lib.coginvasion.cog import SuitBank
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.suit.SuitTournament import SuitTournament
from lib.coginvasion.globals import CIGlobals
import CogBattleGlobals
import random

class DistributedSuitManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory("DistributedSuitManagerAI")

    def __init__(self, air):
        try:
            self.DistributedSuitManagerAI_initialized
            return
        except:
            self.DistributedSuitManagerAI_initialized = 1
        DistributedObjectAI.__init__(self, air)
        self.tournament = SuitTournament(self)
        self.suits = {}
        self.numSuits = 0
        self.activeInvasion = False
        self.suitsSpawnedThisInvasion = 0
        self.lastChoice = None
        self.totalSuitsThisShift = 0
        self.maxSuitsThisShift = 0
        self.spawnerStatus = 0
        self.battle = None
        self.drops = []
        return

    def addDrop(self, drop):
        self.drops.append(drop)

    def removeDrop(self, drop):
        self.drops.remove(drop)

    def getDrops(self):
        return self.drops

    def setBattle(self, battle):
        self.battle = battle

    def getBattle(self):
        return self.battle

    def spawner(self, onOrOff):
        self.spawnerStatus = onOrOff

    def b_spawner(self, onOrOff):
        self.d_spawner(onOrOff)
        self.spawner(onOrOff)

    def d_spawner(self, onOrOff):
        self.sendUpdate('spawner', [onOrOff])

    def getSpawner(self):
        return self.spawnerStatus

    def suitAdminCommand(self, adminToken, commandName):
        avId = self.air.getAvatarIdFromSender()
        tokens = [0, 1, 2]
        av = self.air.doId2do.get(avId, None)
        if av:
            if (adminToken in tokens and
            av.getAdminToken() in tokens and
            av.getAdminToken() == adminToken):
                if commandName in ['invasion', 'suit', 'tournament']:
                    self.createAutoSuit(commandName)
                elif commandName == 'suitSpawner':
                    if self.getSpawner():
                        self.stopSpawner()
                    else:
                        self.startSpawner()
                elif commandName == 'killCogs':
                    self.killAllSuits(1)

    def newShift(self):
        self.maxSuitsThisShift = random.randint(35, 50)
        self.totalSuitsThisShift = 0

    def setActiveInvasion(self, value):
        self.activeInvasion = value

    def getActiveInvasion(self):
        return self.activeInvasion

    def killAllSuits(self, andVP = 0):
        for suit in self.suits.values():
            if not andVP:
                if not suit.isDead() and suit.head != "vp":
                    suit.b_setHealth(0)
            else:
                if not suit.isDead():
                    suit.b_setHealth(0)

    def deadSuit(self, avId):
        if avId in self.suits:
            del self.suits[avId]
        self.numSuits -= 1
        self.battle.b_setCogsRemaining(self.battle.getCogsRemaining() - 1)
        if self.numSuits < 0:
            self.numSuits = 0
        if self.tournament.inTournament:
            self.tournament.handleDeadSuit()
            if not self.tournament.inTournament:
                for avId in self.battle.avIds:
                    avatar = self.air.doId2do.get(avId)
                    if avatar:
                        avatar.questManager.tournamentDefeated(CogBattleGlobals.HoodIndex2HoodName[self.battle.getHoodIndex()])
            return
        if self.numSuits == 0:
            if self.getActiveInvasion():
                for avId in self.battle.avIds:
                    avatar = self.air.doId2do.get(avId)
                    if avatar:
                        avatar.questManager.invasionDefeated(CogBattleGlobals.HoodIndex2HoodName[self.battle.getHoodIndex()])
                self.setActiveInvasion(0)
                self.suitsSpawnedThisInvasion = 0
            #if self.totalSuitsThisShift >= self.maxSuitsThisShift:
            #	self.sendSysMessage(random.choice(CIGlobals.SuitBreakMsgArray))
            #	if self.getSpawner():
            #		self.stopSpawner()
            #	self.startBreak()
            self.sendUpdate('noSuits', [])

    def sendSysMessage(self, message):
        self.sendUpdate('systemMessage', [message])

    def createSuit(self, anySuit = 0, levelRange = None, variant = Variant.NORMAL, plan = None):
        if self.isCogCountFull():
            return
        if anySuit:
            if not levelRange:
                levelRange = CogBattleGlobals.HoodIndex2LevelRange[self.battle.getHoodIndex()]
            availableSuits = []
            level = random.choice(levelRange)
            for suit in SuitBank.getSuits():
                if level >= suit.getLevelRange()[0] and level <= suit.getLevelRange()[1]:
                    availableSuits.append(suit)
            plan = random.choice(availableSuits)
        else:
            if not plan:
                return
            level = random.randint(plan.getLevelRange()[0], plan.getLevelRange()[1])
        if self.battle.getHoodIndex() == CogBattleGlobals.SkeletonHoodIndex:
            variant = Variant.SKELETON
        suit = DistributedSuitAI(self.air)
        suit.setManager(self)
        suit.generateWithRequired(self.zoneId)
        suit.d_setHood(suit.hood)
        suit.b_setLevel(level)
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        if variant == Variant.SKELETON:
            suit.b_setName(CIGlobals.Skelesuit)
        else:
            suit.b_setName(plan.getName())
        #suit.startPosHprBroadcast()
        #suit.d_clearSmoothing()
        #suit.d_broadcastPosHpr()
        suit.b_setParent(CIGlobals.SPHidden)
        self.suits[suit.doId] = suit
        self.numSuits += 1
        if self.numSuits == 1:
            if (self.tournament.inTournament and self.tournament.getRound() == 1
            or not self.tournament.inTournament):
                self.sendUpdate('newSuit', [])
                if self.tournament.inTournament and self.tournament.getRound() == 1:
                    self.sendUpdate('tournamentSpawned', [])
        if self.getActiveInvasion():
            self.suitsSpawnedThisInvasion += 1
            if self.suitsSpawnedThisInvasion == 1:
                if not self.tournament.inTournament:
                    self.sendUpdate('invasionSpawned', [])
        if plan == SuitBank.VicePresident or plan == SuitBank.LucyCrossbill:
            self.sendUpdate('bossSpawned', [])
        return suit

    def requestSuitInfo(self):
        avId = self.air.getAvatarIdFromSender()
        if self.numSuits > 0:
            self.sendUpdateToAvatarId(avId, 'newSuit', [])
        else:
            self.sendUpdateToAvatarId(avId, 'noSuits', [])
        if self.getActiveInvasion() and not self.tournament.inTournament:
            self.sendUpdateToAvatarId(avId, 'invasionSpawned', [])
            self.sendUpdateToAvatarId(avId, 'invasionInProgress', [])
        elif self.tournament.inTournament:
            self.sendUpdateToAvatarId(avId, 'invasionSpawned', [])
            self.sendUpdateToAvatarId(avId, 'tournamentInProgress', [])
            if self.tournament.getRound() == 4:
                self.sendUpdateToAvatarId(avId, 'bossSpawned', [])

    def suitSpawner(self, task):
        configData = [
            base.config.GetBool('want-suit'),
            base.config.GetBool('want-suit-invasion'),
            base.config.GetBool('want-suit-tournament')
        ]
        random_choice = random.randint(0, 7)
        if self.lastChoice == 0 or self.lastChoice == 1 or self.lastChoice == 2 and self.numSuits > 0:
            random_choice = random.randint(2, 6)
        elif self.lastChoice == 7:
            random_choice = random.randint(1, 6)

        if random_choice == 0 or random_choice == 1 or random_choice == 2:
            if configData[2]:
                random_delay = random.randint(40, 80)
                choice = "invasion"
            else:
                self.suitSpawner(task)
                return task.done
        elif random_choice == 3 or random_choice == 4 or random_choice == 5 or random_choice == 6:
            if configData[0]:
                random_delay = random.randint(5, 20)
                choice = "suit"
            else:
                self.suitSpawner(task)
                return task.done
        elif random_choice == 7:
            if configData[1]:
                choice = "tournament"
                random_delay = random.randint(360, 700)
            else:
                self.suitSpawner(task)
                return task.done
        self.lastChoice = random_choice
        if self.lastChoice == 7 and self.getActiveInvasion() or self.numSuits > 0:
            self.lastChoice = 1
            random_delay = random.randint(5, 80)
        if self.air.toonsAreInZone(self.zoneId):
            self.createAutoSuit(choice)
        else:
            random_delay = random.randint(20, 80)
        task.delayTime = random_delay
        return task.again

    def createAutoSuit(self, choice):
        if choice == "invasion":
            if not self.isFullInvasion("large") and not self.tournament.inTournament and not self.getActiveInvasion() and self.numSuits == 0:
                # Spawn invasion
                difficulty = CogBattleGlobals.HoodIndex2LevelRange[self.battle.getHoodIndex()]
                size = random.choice(["small", "medium", "large"])
                suit = "ABC"
                if self.battle.getHoodIndex() == CogBattleGlobals.SkeletonHoodIndex:
                    skeleton = 1
                else:
                    skeleton = 0
                self.startInvasion(suit, difficulty, size, skeleton)
            else:
                self.lastChoice = 3
        elif choice == "suit":
            if not self.isCogCountFull() and not self.tournament.inTournament:
                # Spawn suit
                self.createSuit(anySuit = 1)
        elif choice == "tournament":
            if self.numSuits == 0 and not self.tournament.inTournament and not self.getActiveInvasion():
                # Spawn tournament
                self.tournament.initiateTournament()
            else:
                self.lastChoice = 1

    def isCogCountFull(self):
        return self.numSuits >= 25

    def isFullInvasion(self, size):
        if size == "large":
            return self.numSuits >= 21
        elif size == "medium":
            return self.numSuits >= 14
        elif size == "small":
            return self.numSuits >= 7

    def startInvasion(self, suit, difficulty, size, skeleton, backup = 0):
        if not self.getActiveInvasion() and not self.tournament.inTournament:
            self.sendSysMessage(CIGlobals.SuitInvasionMsg)
        self.setActiveInvasion(1)
        if self.isFullInvasion(size) or self.isCogCountFull():
            return
        taskMgr.add(
            self.__doInvasion, self.uniqueName('doInvasion'),
            extraArgs = [suit, difficulty, size, skeleton, backup], appendTask = True
        )

    def __doInvasion(self, suitType, difficulty, size, skeleton, backup, task):
        if self.isFullInvasion(size) or self.isCogCountFull() or self.suits == None:
            return task.done
        suitsNow = random.randint(0, 7)
        for suit in range(suitsNow):
            if self.isFullInvasion(size) or self.isCogCountFull():
                break
            if suitType == "ABC":
                suitType = random.choice(["A", "B", "C"])
            self.createSuit(levelRange = difficulty, anySuit = 1)
        task.delayTime = 4
        return task.again

    def start(self):
        self.startSpawner()

    def stop(self):
        self.stopSpawner()
        self.stopBreak()
        taskMgr.remove(self.uniqueName('doInvasion'))
        for suit in self.suits.values():
            self.deadSuit(suit.doId)
            suit.disable()
            suit.requestDelete()
        for drop in self.getDrops():
            if hasattr(drop, 'disable'):
                drop.disable()
            drop.requestDelete()

    def startSpawner(self):
        taskMgr.add(self.suitSpawner, self.uniqueName('suitSpawner'))
        self.b_spawner(1)

    def stopSpawner(self):
        taskMgr.remove(self.uniqueName('suitSpawner'))
        self.suitSpawnerOn = False
        self.b_spawner(0)

    def startBreak(self):
        breakTime = random.randint(135, 210)
        self.notify.info("The Suits are taking a break for %s seconds." % str(breakTime))
        taskMgr.doMethodLater(breakTime, self._breakOver, self.uniqueName('suitBreak'))

    def _breakOver(self, task):
        self.newShift()
        if not self.getSpawner():
            self.startSpawner()
        self.notify.info("The Suits are back from break.")
        return task.done

    def stopBreak(self):
        taskMgr.remove(self.uniqueName('suitBreak'))

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.start()

    def disable(self):
        self.stop()
        self.tournament.cleanup()
        self.tournament = None
        self.suits = None
        self.drops = None
        self.numSuits = None
        self.activeInvasion = None
        self.suitsSpawnedThisInvasion = None
        self.lastChoice = None
        self.totalSuitsThisShift = None
        self.maxSuitsThisShift = None
        self.spawnerStatus = None
        self.battle = None

    def delete(self):
        del self.suits
        del self.spawnerStatus
        DistributedObjectAI.delete(self)

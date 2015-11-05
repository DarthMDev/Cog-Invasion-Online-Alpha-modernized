"""

  Filename: DistributedSuitAI.py
  Created by: DecodedLogic (01Sep15)

"""

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.task.Task import Task

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit import CogBattleGlobals
from lib.coginvasion.suit.SuitItemDropper import SuitItemDropper
from lib.coginvasion.cog import SuitBank
from lib.coginvasion.cog import SuitGlobals
from lib.coginvasion.cog.SpawnMode import SpawnMode
from lib.coginvasion.cog.SuitBrainAI import SuitBrain
from lib.coginvasion.cog import SuitAttacks
from lib.coginvasion.cog.SuitBank import SuitPlan
from lib.coginvasion.cog.SuitRandomStrollBehavior import SuitRandomStrollBehavior
from lib.coginvasion.cog.SuitPanicBehavior import SuitPanicBehavior
from lib.coginvasion.cog.SuitAttackBehavior import SuitAttackBehavior
from lib.coginvasion.cog import Variant
import types, random
from lib.coginvasion.cog.SuitFlyToRandomSpotBehavior import SuitFlyToRandomSpotBehavior
from lib.coginvasion.cog.SuitCallInBackupBehavior import SuitCallInBackupBehavior

class DistributedSuitAI(DistributedAvatarAI, DistributedSmoothNodeAI):
    notify = directNotify.newCategory('DistributedSuitAI')

    def __init__(self, air):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        self.anim = 'neutral'
        self.brain = None
        self.track = None
        self.currentPath = None
        self.currentPathQueue = []
        self.suitMgr = None
        self.suitPlan = 0
        self.variant = Variant.NORMAL
        self.itemDropper = SuitItemDropper(self)
        self.suitState = 0
        self.startPoint = -1
        self.endPoint = -1
        self.stateTimestamp = 0
        self.level = 0
        self.lateX = 0
        self.lateY = 0
        self.healthChangeEvent = SuitGlobals.healthChangeEvent
        self.animStateChangeEvent = SuitGlobals.animStateChangeEvent
        self.requestedBehaviors = []
        
        # This is for handling death.
        self.deathAnim = None
        self.deathTimeLeft = 0

    def b_setSuit(self, plan, variant = 0):
        self.d_setSuit(plan, variant)
        self.setSuit(plan, variant)

    def d_setSuit(self, plan, variant = 0):
        if isinstance(plan, SuitPlan):
            plan = SuitBank.getIdFromSuit(plan)
        self.sendUpdate('setSuit', [plan, variant])

    def setSuit(self, plan, variant = 0, tutorial = None):
        self.suitPlan = plan
        self.variant = Variant.getVariantById(variant)
        self.maxHealth = CIGlobals.getSuitHP(self.level)
        self.health = self.maxHealth
        self.itemDropper.calculate(tutorial)

        if self.level == 0:
            self.maxHealth = 1
            self.health = self.maxHealth

    def getSuit(self):
        return tuple((self.suitPlan, self.variant))

    def setSuitState(self, index, startPoint, endPoint):
        if index == 0:
            self.setLatePos(self.getX(render), self.getY(render))
        self.suitState = index
        self.startPoint = startPoint
        self.endPoint = endPoint

    def d_setSuitState(self, index, startPoint, endPoint):
        self.stateTimestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setSuitState', [index, startPoint, endPoint, self.stateTimestamp])

    def b_setSuitState(self, index, startPoint, endPoint):
        self.d_setSuitState(index, startPoint, endPoint)
        self.setSuitState(index, startPoint, endPoint)

    def getSuitState(self):
        return [self.suitState, self.startPoint, self.endPoint, self.stateTimestamp]

    def setAnimState(self, anim):
        if hasattr(self, 'animStateChangeEvent'):
            messenger.send(self.animStateChangeEvent, [anim, self.anim])
            self.anim = anim
            if type(self.anim) == types.IntType:
                if anim != 44 and anim != 45:
                    self.anim = SuitGlobals.getAnimById(anim).getName()
                elif anim == 44:
                    self.anim = 'die'
                elif anim == 45:
                    self.anim = 'flyNeutral'

    def b_setAnimState(self, anim):
        if type(anim) == types.StringType:
            animId = SuitGlobals.getAnimId(SuitGlobals.getAnimByName(anim))
            if animId == None and anim != 'flyNeutral':
                animId = 44
            elif anim == 'flyNeutral':
                animId = 45
        else:
            animId = anim
        self.d_setAnimState(animId)
        self.setAnimState(animId)

    def d_setAnimState(self, anim):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [anim, timestamp])

    def getAnimState(self):
        return self.anim

    def d_startMoveInterval(self, startPos, endPos, durationFactor = 0.2):
        durationFactor = durationFactor * 10
        self.sendUpdate('startMoveInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), durationFactor])

    def d_stopMoveInterval(self):
        self.sendUpdate('stopMoveInterval', [])

    def d_startProjInterval(self, startPos, endPos, duration, gravityMult):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startProjInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), duration, gravityMult, timestamp])

    def d_startPosInterval(self, startPos, endPos, duration, blendType):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('startPosInterval', [startPos.getX(), startPos.getY(), startPos.getZ(),
                endPos.getX(), endPos.getY(), endPos.getZ(), duration, blendType, timestamp])

    def setLatePos(self, lateX, lateY):
        self.lateX = lateX
        self.lateY = lateY

    def getLatePos(self):
        return [self.lateX, self.lateY]

    def setLevel(self, level):
        self.level = level

    def d_setLevel(self, level):
        self.sendUpdate('setLevel', [level])

    def b_setLevel(self, level):
        self.setLevel(level)
        self.d_setLevel(level)

    def getLevel(self):
        return self.level

    def setHealth(self, health):
        prevHealth = self.health
        DistributedAvatarAI.setHealth(self, health)
        messenger.send(self.healthChangeEvent, [health, prevHealth])

    def monitorHealth(self, task):
        if self.health <= 0:
            if hasattr(self, 'brain'):
                self.brain.stopThinking()
                self.brain.unloadBehaviors()
                self.brain = None
            self.b_setSuitState(0, -1, -1)
            currentAnim = SuitGlobals.getAnimByName(self.anim)
            self.clearTrack()
            if currentAnim:
                if not self.deathAnim:
                    self.deathAnim = currentAnim
                    self.deathTimeLeft = currentAnim.getDeathHoldTime()
                    taskMgr.add(self.__handleDeath, 'Handle Suit Defeat')
            else:
                self.killSuit()
            return Task.done
        return Task.cont
    
    def __handleDeath(self, task):
        task.delayTime = 1
        if self.anim != self.deathAnim:
            currentAnim = SuitGlobals.getAnimByName(self.anim)
            if currentAnim:
                delayTime = currentAnim.getDeathHoldTime()
                self.deathTimeLeft += int(delayTime / 2)
        if self.deathTimeLeft == 0:
            self.killSuit()
            return Task.done
        else:
            self.deathTimeLeft--
            return Task.cont

    def handleAvatarDefeat(self, av):
        if av.isDead() and hasattr(self, 'brain'):
            self.b_setAnimState('win')
            self.brain.stopThinking()
            taskMgr.doMethodLater(6.0, self.brain.startThinking, self.uniqueName('Resume Thinking'))

    def disableMovement(self):
        self.brain.stopThinking()

    def enableMovement(self):
        self.brain.startThinking()

    def addBehavior(self, behavior, priority):
        self.requestedBehaviors.append([behavior, priority])

    def toonHitByWeapon(self, weaponId, avId):
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup", "buzzword", "razzledazzle",
                        "jargon", "mumbojumbo", 'doubletalk', 'schmooze', 'fingerwag', 'filibuster']:
            self.d_handleWeaponTouch()
        dmg = int(self.maxHealth / SuitAttacks.SuitAttackDamageFactors[weapon])
        toon = self.air.doId2do.get(avId, None)
        if toon:
            hp = toon.getHealth() - dmg
            if hp < 0:
                hp = 0
            toon.b_setHealth(hp)
            toon.d_announceHealth(0, dmg)
            self.handleAvatarDefeat(toon)

    def turretHitByWeapon(self, weaponId, avId):
        weapon = SuitAttacks.SuitAttackLengths.keys()[weaponId]
        if not weapon in ["pickpocket", "fountainpen", "hangup"]:
            self.d_handleWeaponTouch()
        dmg = int(self.maxHealth / SuitAttacks.SuitAttackDamageFactors[weapon])
        turret = self.air.doId2do.get(avId, None)
        if turret:
            turret.b_setHealth(turret.getHealth() - 1)
            turret.d_announceHealth(0, dmg)
            self.handleAvatarDefeat(turret)

    def d_handleWeaponTouch(self):
        self.sendUpdate('handleWeaponTouch', [])

    def d_interruptAttack(self):
        self.sendUpdate('interruptAttack', [])

    def killSuit(self):
        if self.level > 0 and self.health <= 0:
            print self.health
            self.b_setAnimState('die')
            self.clearTrack()
            self.track = Sequence(Wait(6.0), Func(self.closeSuit))
            self.track.start()

    def closeSuit(self):
        self.itemDropper.drop()
        if self.getManager():
            self.getManager().deadSuit(self.doId)
        self.disable()
        self.requestDelete()

    def spawn(self, spawnMode = SpawnMode.FLYDOWN):
        self.brain = SuitBrain(self)
        for behavior, priority in self.requestedBehaviors:
            self.brain.addBehavior(behavior, priority)
        self.requestedBehaviors = []
        self.brain.addBehavior(SuitAttackBehavior(self), priority = 3)
        if self.suitPlan.getName() != SuitGlobals.VicePresident:
            self.brain.addBehavior(SuitPanicBehavior(self), priority = 2)
        else:
            self.brain.addBehavior(SuitFlyToRandomSpotBehavior(self), priority = 2)
            self.brain.addBehavior(SuitCallInBackupBehavior(self), priority = 4)
        self.brain.addBehavior(SuitRandomStrollBehavior(self), priority = 1)
        place = CIGlobals.SuitSpawnPoints[self.hood]
        landspot = random.choice(place.keys())
        path = place[landspot]
        index = place.keys().index(landspot)
        self.currentPath = landspot
        self.setH(random.uniform(0.0, 360.0))
        self.clearTrack()
        self.track = Sequence()
        if spawnMode == SpawnMode.FLYDOWN:
            flyTrack = self.posInterval(3,
                path, startPos = path + (0, 0, 50)
            )
            flyTrack.start()
            self.b_setSuitState(2, index, index)
            self.track.append(Wait(5.4))
        self.track.append(Func(self.b_setAnimState, 'neutral'))
        self.track.append(Wait(1.0))
        self.track.append(Func(self.brain.startThinking))
        self.track.start()
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def clearTrack(self):
        if self.track:
            self.track.pause()
            self.track = None

    def setManager(self, suitMgr):
        self.suitMgr = suitMgr
        self.hood = CogBattleGlobals.HoodIndex2HoodName[self.getManager().getBattle().getHoodIndex()]

    def getManager(self):
        if hasattr(self, 'suitMgr'):
            return self.suitMgr
        return None

    def generate(self):
        DistributedAvatarAI.generate(self)
        DistributedSmoothNodeAI.generate(self)

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        self.clearTrack()
        self.track = Sequence(Wait(0.1), Func(self.spawn))
        self.track.start()

    def disable(self):
        DistributedAvatarAI.disable(self)
        self.clearTrack()
        taskMgr.remove(self.uniqueName('monitorHealth'))
        if self.brain:
            self.brain.stopThinking()
            self.brain = None
        self.itemDropper.cleanup()
        self.itemDropper = None
        self.lateX = None
        self.lateY = None
        self.anim = None
        self.currentPath = None
        self.currentPathQueue = None
        self.suitState = None
        self.suitPlan = None
        self.variant = None
        self.stateTimestamp = None
        self.startPoint = None
        self.endPoint = None
        self.level = None
        self.suitMgr = None
        self.healthChangeEvent = None
        self.animStateChangeEvent = None
        self.requestedBehaviors = None
        self.deathAnim = None
        self.deathTimeLeft = None

    def delete(self):
        self.DELETED = True
        del self.brain
        del self.itemDropper
        del self.lateX
        del self.lateY
        del self.anim
        del self.currentPath
        del self.currentPathQueue
        del self.suitState
        del self.suitPlan
        del self.variant
        del self.stateTimestamp
        del self.startPoint
        del self.endPoint
        del self.level
        del self.suitMgr
        del self.healthChangeEvent
        del self.animStateChangeEvent
        del self.requestedBehaviors
        del self.track
        del self.deathAnim
        del self.deathTimeLeft
        DistributedAvatarAI.delete(self)
        DistributedSmoothNodeAI.delete(self)

    def printPos(self, task):
        print '%s\n%s' % (self.getPos(render), self.getHpr(render))
        return Task.cont

    def getBrain(self):
        return self.brain

    def setCurrentPath(self, curPath):
        self.currentPath = curPath

    def getCurrentPath(self):
        return self.currentPath

    def getCurrentPathQueue(self):
        return self.currentPathQueue

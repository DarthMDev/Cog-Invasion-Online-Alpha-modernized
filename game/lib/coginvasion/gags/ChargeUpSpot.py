"""

  Filename: ChargeUpSpot.py
  Created by: DecodedLogic (17Aug15)

"""

from lib.coginvasion.gags.LocationSeeker import LocationSeeker
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpScaleInterval, SoundInterval
from direct.interval.IntervalGlobal import Func, LerpColorScaleInterval
from direct.task.Task import Task
from panda3d.core import VBase4

class ChargeUpSpot(LocationSeeker):
    
    def __init__(self, avatar, selectionRadius, minDistance, maxDistance, shadowScale, maxCogs = 4):
        LocationSeeker.__init__(self, avatar, minDistance, maxDistance, shadowScale)
        self.pollMouseTaskName = 'Poll Mouse Hold Downs'
        self.chargedUpName = 'Charged Up'
        self.chargedCancelName = 'Charge Canceled'
        self.mouseDownName = 'mouse1-down'
        self.chargingSfxPath = 'phase_4/audio/sfx/MG_sfx_ice_scoring_1.mp3'
        self.chargingSfx = base.audio3d.loadSfx(self.chargingSfxPath)
        self.tickSfxPath = 'phase_13/audio/sfx/tick_counter_short.mp3'
        self.tickSfx = base.audio3d.loadSfx(self.tickSfxPath)
        self.lMouseDn = None
        self.isCharging = False
        self.shadowTrack = None
        self.chargeDuration = 2.5
        self.selectionRadius = selectionRadius
        self.maxCogs = maxCogs
        self.selectedCogs = []
        
    def buildShadow(self):
        self.cleanupShadow()
        if not self.dropShadowPath or not self.avatar: return
        self.dropShadow = loader.loadModel('phase_4/models/minigames/ice_game_score_circle.bam')
        self.dropShadow.setScale(self.shadowScale)
        self.dropShadow.setAlphaScale(0.5)
        self.dropShadow.setTransparency(1)
        
    def startSeeking(self):
        LocationSeeker.startSeeking(self)
        if not self.dropShadow:
            return
        
        # Let's actually ignore LEFT mouse clicks.
        self.avatar.ignore('mouse1')
        
        # Instead, let's start listening to LEFT mouse hold downs.
        self.lMouseDn = inputState.watch(self.mouseDownName, 'mouse1', 'mouse1-up')
        base.taskMgr.add(self.__pollMouseHeldDown, self.pollMouseTaskName)
        
    def __selectNearbyCogs(self):
        self.selectedCogs = []
        for obj in base.cr.doId2do.values():
            if obj.__class__.__name__ == 'DistributedSuit':
                if obj.getPlace() == self.avatar.zoneId:
                    if obj.getDistance(self.dropShadow) <= self.selectionRadius:
                        if self.avatar.doId == self.avatar.doId:
                            if len(self.selectedCogs) < self.maxCogs:
                                if not obj.isDead():
                                    self.selectedCogs.append(obj)
    
    """ This returns a track that 
        does a quick red flash effect with a sound. """
                                
    def __tickNearbyCogs(self):
        self.__selectNearbyCogs()
        tickTrack = Parallel()
        tickDuration = 0.4
        
        for cog in self.selectedCogs:
            base.audio3d.attachSoundToObject(self.tickSfx, cog)
            tickTrack.append(Parallel(Sequence(
                LerpColorScaleInterval(cog, tickDuration, VBase4(1, 0, 0, 1)),
                Func(cog.clearColorScale),
                Func(cog.d_disableMovement)
            ), SoundInterval(self.tickSfx, duration = tickDuration)))
        return tickTrack
        
    def startCharging(self):
        # Let's disable shadow movement.
        LocationSeeker.stopSeeking(self)
        self.dropShadow.setZ(self.dropShadow.getZ() - 0.45)
        
        # Let's start the charging effect.
        finalScale = 6
        self.shadowTrack = Sequence()
        chargeTrack = Parallel(
            LerpScaleInterval(
                self.dropShadow,
                self.chargeDuration,
                finalScale,
                startScale = self.dropShadow.getScale(),
                blendType = 'easeInOut'
            ),
            Func(base.audio3d.attachSoundToObject, self.chargingSfx, self.dropShadow),
            SoundInterval(self.chargingSfx, duration = self.chargeDuration)
        )
        self.shadowTrack.append(chargeTrack)
        self.shadowTrack.append(self.__tickNearbyCogs())
        self.shadowTrack.append(Func(self.onFullCharge))
        self.shadowTrack.start()
        self.isCharging = True
        
    def onFullCharge(self):
        LocationSeeker.cleanupShadow(self)
        if self.shadowTrack:
            self.shadowTrack.finish()
            self.shadowTrack = None
        messenger.send(self.chargedUpName)
        
    def stopCharging(self):
        self.isCharging = False
        if self.shadowTrack:
            self.shadowTrack.pause()
        if hasattr(self, 'selectedCogs'):
            for cog in self.selectedCogs:
                cog.clearColorScale()
        base.taskMgr.remove(self.pollMouseTaskName)
        messenger.send(self.chargedCancelName)
        if hasattr(self, 'lMouseDn'):
            if self.lMouseDn:
                self.lMouseDn.release()
        LocationSeeker.cleanupShadow(self)
        
    def cleanup(self):
        base.audio3d.detachSound(self.chargingSfx)
        base.audio3d.detachSound(self.tickSfx)
        self.chargingSfx.stop()
        self.tickSfx.stop()
        if self.isCharging:
            self.stopCharging()
        if self.shadowTrack:
            self.shadowTrack.pause()
            self.shadowTrack = None
        del self.isCharging
        del self.mouseDownName
        del self.pollMouseTaskName
        del self.chargedUpName
        del self.chargedCancelName
        del self.lMouseDn
        del self.chargingSfx
        del self.chargingSfxPath
        del self.tickSfx
        del self.tickSfxPath
        del self.selectionRadius
        del self.selectedCogs
        del self.maxCogs
        LocationSeeker.cleanup(self)
        
    def __pollMouseHeldDown(self, task):
        if not hasattr(self, 'mouseDownName'):
            return Task.done
        if inputState.isSet(self.mouseDownName) and not self.isCharging:
            self.startCharging()
        elif not inputState.isSet(self.mouseDownName) and self.isCharging:
            if self.selectedCogs == 0:
                self.stopCharging()
        return Task.cont
    
    def getSelectedCogs(self):
        return self.selectedCogs
    
    def getChargedUpName(self):
        return self.chargedUpName
    
    def getChargedCanceledName(self):
        return self.chargedCancelName
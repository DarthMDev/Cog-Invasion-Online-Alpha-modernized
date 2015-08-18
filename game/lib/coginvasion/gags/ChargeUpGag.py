"""

  Filename: ChargeUpGag.py
  Created by: DecodedLogic (17Aug15)

"""

from lib.coginvasion.gags.ChargeUpSpot import ChargeUpSpot
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func
from direct.interval.IntervalGlobal import Wait, SoundInterval

class ChargeUpGag:
    
    def __init__(self, selectionRadius, minDistance, maxDistance, shadowScale, maxCogs = 4):
        self.avatar = None
        self.selectionRadius = selectionRadius
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.shadowScale = shadowScale
        self.maxCogs = maxCogs
        self.chargeUpSpot = None
        
        self.buttonSfxPath = 'phase_5/audio/sfx/AA_drop_trigger_box.mp3'
        self.buttonSfx = None
        self.buttonAnim = 'push-button'
        self.button = None
        self.buttonHold = 0.5
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.actorTrack = None
        self.soundTrack = None
        self.selectedCogs = []
        
    def start(self, avatar):
        self.cleanupChargeUpSpot()
        self.avatar = avatar
        self.buildButton()
        self.button.reparentTo(self.avatar.find('**/def_joint_left_hold'))
        track = Sequence(ActorInterval(self.avatar, self.buttonAnim, startFrame = 0, endFrame = self.chooseLocFrame, 
                                       playRate = self.playRate))
        if self.avatar == base.localAvatar:
            self.chargeUpSpot = ChargeUpSpot(self.avatar, self.selectionRadius,
                                              self.minDistance, self.maxDistance, self.shadowScale, self.maxCogs)
            self.avatar.acceptOnce(self.chargeUpSpot.getChargedUpName(), base.localAvatar.releaseGag)
            track.append(Func(self.chargeUpSpot.startSeeking))
        track.start()
        
    def release(self):
        if self.avatar:
            self.selectedCogs = self.chargeUpSpot.getSelectedCogs()
            self.cleanupChargeUpSpot()
            self.buildTracks()
        
    def complete(self):
        numFrames = base.localAvatar.getNumFrames(self.buttonAnim)
        ActorInterval(self.avatar, self.buttonAnim, startFrame = self.completeFrame, endFrame = numFrames,
                      playRate = self.playRate).start()
        self.cleanupButton()
        
    def buildTracks(self):
        if not self.avatar: 
            return
        self.cleanupTracks()
        self.actorTrack = Sequence(ActorInterval(self.avatar, self.buttonAnim, startFrame = self.chooseLocFrame,
                           endFrame = self.completeFrame, playRate = self.playRate))
        self.soundTrack = Sequence(Wait(self.buttonHold), SoundInterval(self.buttonSfx, self.avatar))
        self.actorTrack.start()
        self.soundTrack.start()
            
    def cleanupTracks(self):
        if self.actorTrack:
            self.actorTrack.pause()
            self.actorTrack = None
        if self.soundTrack:
            self.soundTrack.pause()
            self.soundTrack = None

    def getActorTrack(self):
        return self.actorTrack
    
    def getSoundTrack(self):
        return self.soundTrack
    
    def getSelectedCogs(self):
        return self.selectedCogs
        
    def buildButton(self):
        self.cleanupButton()
        self.button = loader.loadModel('phase_3.5/models/props/button.bam')
        
    def cleanupButton(self):
        if self.button:
            self.button.removeNode()
            self.button = None
        
    def cleanupChargeUpSpot(self):
        if self.chargeUpSpot:
            self.chargeUpSpot.cleanup()
            self.chargeUpSpot = None
            
    def cleanup(self):
        self.cleanupButton()
        self.cleanupChargeUpSpot()
        self.buttonSfx.stop()
        del self.buttonSfxPath
        del self.buttonSfx
        del self.avatar
        del self.selectionRadius
        del self.minDistance
        del self.maxDistance
        del self.shadowScale
        del self.maxCogs
        del self.buttonAnim
        del self.buttonHold
        del self.chooseLocFrame
        del self.completeFrame
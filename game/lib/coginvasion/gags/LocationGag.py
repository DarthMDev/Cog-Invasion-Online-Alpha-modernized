"""

  Filename: LocationGag.py
  Created by: DecodedLogic (24Jul15)

"""

from LocationSeeker import LocationSeeker
from direct.interval.IntervalGlobal import Sequence, Func, Parallel, SoundInterval, Wait
from direct.gui.DirectGui import OnscreenText
from panda3d.core import Point3
from lib.coginvasion.globals import CIGlobals

class LocationGag:

    def __init__(self, minDistance, maxDistance, shadowScale = 1):
        self.buttonSoundPath = 'phase_5/audio/sfx/AA_drop_trigger_box.mp3'
        self.button = None
        self.buttonSfx = loader.loadSfx(self.buttonSoundPath)
        self.buttonAnim = 'push-button'
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.avatar = None
        self.dropLoc = None
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.locationSeeker = None
        self.buttonHold = 0.6
        self.actorTrack = None
        self.soundTrack = None
        self.isCircle = False
        self.shadowScale = 1
        self.helpInfo = None

    def setShadowData(self, isCircle, shadowScale):
        self.isCircle = isCircle
        self.shadowScale = shadowScale

    def getShadowScale(self):
        return self.shadowScale

    def start(self, avatar):
        self.avatar = avatar
        self.cleanupLocationSeeker()
        self.buildButton()
        self.button.reparentTo(self.avatar.find('**/def_joint_left_hold'))
        buttonAnimDuration = self.avatar.getDuration(self.buttonAnim, toFrame = self.chooseLocFrame)
        
        track = Parallel(
            Sequence(Func(self.avatar.setPlayRate, self.playRate, self.buttonAnim),
            Func(self.avatar.play, self.buttonAnim, toFrame = self.chooseLocFrame),
            Wait(buttonAnimDuration),
            Func(self.avatar.pose, self.buttonAnim, self.chooseLocFrame))
        )
        if self.avatar == base.localAvatar:
            self.locationSeeker = LocationSeeker(self.avatar, self.minDistance, self.maxDistance)
            self.locationSeeker.setShadowType(self.isCircle, self.shadowScale)
            self.avatar.acceptOnce(self.locationSeeker.getLocationSelectedName(), base.localAvatar.releaseGag)
            track.append(Sequence(Func(self.locationSeeker.startSeeking)))

            self.helpInfo = OnscreenText(text = 'Move the shadow with your mouse\nClick to release',
                pos = (0, -0.75), font = CIGlobals.getToonFont(), fg = (1, 1, 1, 1),
                shadow = (0, 0, 0, 1))

        track.start()

    def release(self):
        if self.avatar:
            self.cleanupLocationSeeker()
            self.buildTracks()

    def complete(self):
        if self.button:
            numFrames = base.localAvatar.getNumFrames(self.buttonAnim)
            waitDuration = self.avatar.getDuration(self.buttonAnim, fromFrame = self.completeFrame, toFrame = numFrames)
            Sequence(Func(self.avatar.setPlayRate, self.playRate, self.buttonAnim),
                Func(self.avatar.play, self.buttonAnim, fromFrame = self.completeFrame, toFrame = numFrames),
                Wait(waitDuration)
            )
        self.cleanupButton()

    def buildTracks(self, mode=0):
        if not self.avatar:
            return
        self.cleanupTracks()
        if mode == 0:
            waitDuration = self.avatar.getDuration(self.buttonAnim, fromFrame = self.chooseLocFrame, toFrame = self.completeFrame)
            self.actorTrack = Sequence(Func(self.avatar.setPlayRate, self.playRate, self.buttonAnim),
                Func(self.avatar.play, self.buttonAnim, fromFrame = self.chooseLocFrame, toFrame = self.completeFrame),
                Wait(waitDuration)
            )
            self.soundTrack = Sequence(Wait(self.buttonHold), SoundInterval(self.buttonSfx, node = self.avatar))

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

    def setDropLoc(self, x, y, z):
        self.dropLoc = Point3(x, y, z)

    def buildButton(self):
        self.cleanupButton()
        self.button = loader.loadModel('phase_3.5/models/props/button.bam')

    def setLocation(self, value):
        self.dropLoc = value

    def getLocation(self):
        return self.dropLoc
    
    def getLocationSeeker(self):
        return self.locationSeeker

    def cleanupButton(self):
        if self.button:
            self.button.removeNode()
            self.button = None

    def cleanupLocationSeeker(self):
        if self.locationSeeker:
            self.dropLoc = self.locationSeeker.getLocation()
            self.locationSeeker.cleanup()
            self.locationSeeker = None
        if self.helpInfo:
            self.helpInfo.destroy()

    def cleanup(self):
        LocationSeeker.cleanup(self)
        self.cleanupButton()
        self.cleanupLocationSeeker()
        self.cleanupTracks()
        self.dropLoc = None
        self.buttonSfx.stop()
        self.buttonSoundPath = None
        self.buttonAnim = None
        self.avatar = None

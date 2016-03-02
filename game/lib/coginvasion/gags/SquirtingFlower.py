########################################
# Filename: SquirtingFlower.py
# Created by: DecodedLogic (22Feb16)
########################################
from lib.coginvasion.gags.SquirtGag import SquirtGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals

from direct.interval.IntervalGlobal import Sequence, Func, Wait, Parallel
from direct.interval.IntervalGlobal import LerpScaleInterval

from panda3d.core import Point3

class SquirtingFlower(SquirtGag):
    
    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.SquirtFlower, GagGlobals.getProp(3.5, 'button'), 
            3, GagGlobals.FLOWER_HIT_SFX, GagGlobals.FLOWER_HIT_SFX, GagGlobals.NULL_SFX, None, 0, 0, 0)
        self.setImage('phase_3.5/maps/squirting-flower.png')
        self.flower = None
        self.flowerScale = 1.5
        self.track = Parallel()
        self.timeout = 4.0
        
    def start(self):
        SquirtGag.start(self)
        self.buildFlower()
        self.build()
        self.equip()
        
        if self.isLocal():
            self.startTimeout()
        self.origin = self.getSprayStartPos()
        
        def attachFlower():
            flowerJoint = self.avatar.find('**/def_joint_attachFlower')
            if flowerJoint.isEmpty():
                flowerJoint = self.avatar.find('**/joint_attachFlower')
            self.flower.reparentTo(flowerJoint)
            self.flower.setY(self.flower.getY() + 4)
        
        # The variables we'll need.
        totalAnimationTime = 2.5
        flowerAppear = 1.0
        flowerScaleTime = 0.5
        
        # Let's start building the track.
        animTrack = Sequence(
            Func(self.avatar.play, 'push-button'),
            Wait(self.avatar.getDuration('push-button'))
        )
        self.track.append(animTrack)
        
        flowerTrack = Sequence(
            Func(attachFlower),
            Wait(flowerAppear),
            LerpScaleInterval(self.flower, flowerScaleTime, 
                1.5, startScale = GagGlobals.PNT3NEAR0),
            Wait(totalAnimationTime - flowerScaleTime - flowerAppear)
        )
        flowerTrack.append(Func(self.release))
        flowerTrack.append(LerpScaleInterval(self.flower, flowerScaleTime, GagGlobals.PNT3NEAR0))
        flowerTrack.append(LerpScaleInterval(self.gag, flowerScaleTime, GagGlobals.PNT3NEAR0))
        flowerTrack.append(Func(self.unEquip))
        self.track.append(flowerTrack)
        self.track.start()
        
    def getSprayStartPos(self):
        if not self.avatar.isEmpty() and not self.flower.isEmpty():
            self.avatar.update(0)
            return self.flower.getPos(render)
        
    def release(self):
        SquirtGag.release(self)
        if not self.avatar.isEmpty() and self.gag:
            self.sprayJoint = self.flower.find('**/joint_attachSpray')
            self.sprayRange = self.avatar.getPos(render) + Point3(0, GagGlobals.SELTZER_RANGE, 0)
            self.doSpray(0.2, 0.2, 0.1)
            if self.isLocal():
                base.localAvatar.sendUpdate('usedGag', [self.id])
                
    def unEquip(self):
        SquirtGag.unEquip(self)
        self.cleanup()
        self.reset()
                
    def cleanup(self):
        if self.flower:
            self.flower.removeNode()
            self.flower = None
        if self.track:
            self.track.pause()
            self.track = Parallel()
        
    def setHandJoint(self):
        if self.avatar:
            self.handJoint = self.avatar.find('**/joint_Lhold')
    
    def buildFlower(self):
        if self.flower:
            self.flower.removeNode()
            self.flower = None
        self.flower = loader.loadModel(GagGlobals.getProp(3.5, 'squirting-flower'))
        self.flower.setScale(GagGlobals.PNT3NEAR0)
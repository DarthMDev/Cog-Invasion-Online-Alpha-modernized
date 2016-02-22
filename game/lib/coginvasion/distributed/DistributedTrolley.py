########################################
# Filename: DistributedTrolley.py
# Created by: blach (??Jul14)
########################################

from lib.coginvasion.globals import CIGlobals
from direct.distributed.DistributedNode import DistributedNode
from direct.gui.DirectGui import *
from direct.directnotify.DirectNotify import DirectNotify
from pandac.PandaModules import *
from panda3d.core import *
import random

notify = DirectNotify().newCategory("DistributedTrolley")

class DistributedTrolley(DistributedNode):
	def __init__(self, cr):
		self.cr = cr
		DistributedNode.__init__(self, cr)
		NodePath.__init__(self, 'trolley')
		
		self.destination = ""
		
		self.filledSpots = 0
		self.leaving = False
		self.gone = False
		
		self.destination_lbl = None
		
		self.movingSfx = loader.loadSfx("phase_4/audio/sfx/SZ_trolley_away.ogg")
		self.bellSfx = loader.loadSfx("phase_4/audio/sfx/SZ_trolley_bell.ogg")
	def setDestination(self, destination):
		try:
			self.destination_lbl.remove()
			self.destination_lbl = None
		except:
			pass
		self.destination = destination
		notify.info("Trolley destination set to %s" % (self.destination))
		mf = loader.loadFont("phase_3/models/fonts/MickeyFont.bam")
		self.destination_lbl = DirectLabel(text=self.destination, scale=1, text_wordwrap=8, text_decal=True, relief=None, text_font=mf, text_fg=(1,0,0,1), parent=self.trolleyStation, pos=(15,5,10))
	def b_setDestination(self, destination):
		self.d_setDestination(destination)
		self.setDestination(destination)
	def d_setDestination(self, destination):
		self.sendUpdate("setDestination", [destination])
	def getDestination(self):
		return self.destination
		
	def setFilledSpots(self, spots):
		self.filledSpots = spots
	def b_setFilledSpots(self, spots):
		self.d_setFilledSpots(spots)
		self.setFilledSpots(spots)
	def d_setFilledSpots(self, spots):
		self.sendUpdate("setFilledSpots", [spots])
	def getFilledSpots(self):
		return self.filledSpots
		
	def isGone(self):
		return self.gone
	def isLeaving(self):
		return self.leaving
		
	def initCollisions(self):
		ss = CollisionSphere(0, 0, 0, 10)
		snode = CollisionNode('trolleySensor')
		snode.addSolid(ss)
		self.snp = self.trolleyCar.attachNewNode(snode)
		self.snp.setCollideMask(BitMask32(0))
		self.snp.node().setFromCollideMask(BitMask32(3))
		self.snp.setZ(3)
		
		self.snp.show()
		
		event = CollisionHandlerEvent()
		event.setInPattern("%fn-into")
		event.setOutPattern("%fn-out")
		base.cTrav.addCollider(self.snp, event)

	def generate(self):
		DistributedNode.generate(self)
		
		self.trolleyStation = self.cr.getCurrentHood().geom.find('**/*trolley_station*')
		self.trolleyCar = self.trolleyStation.find('**/trolley_car')
		
	def disable(self):
		DistributedNode.disable(self)
		del self.trolleyStation
		del self.trolleyCar
		return
	def delete(self):
		DistributedNode.delete(self)
		del self.movingSfx
		del self.bellSfx

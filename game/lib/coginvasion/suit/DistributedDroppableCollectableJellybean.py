"""

  Filename: DistributedDroppableCollectableJellybean.py
  Created by: blach (22Mar15)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeans import DistributedDroppableCollectableJellybeans
from direct.interval.IntervalGlobal import *
import random

class DistributedDroppableCollectableJellybean(DistributedDroppableCollectableJellybeans):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybean")
	
	def __init__(self, cr):
		DistributedDroppableCollectableJellybeans.__init__(self, cr)
		self.bean = None
		self.spinIval = None
		self.tickSfx = None
		
	def loadObject(self):
		self.removeObject()
		self.bean = loader.loadModel("phase_5.5/models/estate/jellyBean.bam")
		self.bean.setTwoSided(1)
		self.bean.setScale(1.5)
		self.bean.setZ(1.5)
		self.bean.reparentTo(self)
		# Give the bean a completely random color.
		self.bean.setColor(
			VBase4(
				random.uniform(0, 1),
				random.uniform(0, 1),
				random.uniform(0, 1),
				1.0
			)
		)
		self.spin()
		
	def removeObject(self):
		if self.bean:
			self.bean.removeNode()
			self.bean = None
	
	def handleCollisions(self, entry):
		SoundInterval(self.tickSfx).start()
		DistributedDroppableCollectableJellybeans.handleCollisions(self, entry)
	
	def load(self):
		self.tickSfx = base.loadSfx("phase_3.5/audio/sfx/tick_counter.mp3")
		self.collectSfx = base.loadSfx("phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.mp3")
		DistributedDroppableCollectableJellybeans.load(self)
		
	def unload(self):
		self.tickSfx = None
		self.stopSpin()
		DistributedDroppableCollectableJellybeans.unload(self)
			
	def spin(self):
		self.stopSpin()
		self.spinIval = LerpHprInterval(
			self.bean,
			duration = 3.0,
			hpr = Vec3(360, 0, 0),
			startHpr = (0, 0, 0),
		)
		self.spinIval.loop()
		
	def stopSpin(self):
		if self.spinIval:
			self.spinIval.finish()
			self.spinIval = None

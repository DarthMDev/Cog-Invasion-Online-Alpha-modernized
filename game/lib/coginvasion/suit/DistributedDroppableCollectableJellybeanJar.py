"""

  Filename: DistributedDroppableCollectableJellybeanJar.py
  Created by: blach (22Mar15)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeans import DistributedDroppableCollectableJellybeans
from direct.interval.IntervalGlobal import *

class DistributedDroppableCollectableJellybeanJar(DistributedDroppableCollectableJellybeans):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeanJar")

	def __init__(self, cr):
		DistributedDroppableCollectableJellybeans.__init__(self, cr)
		self.jar = None
		self.tickSfx = None

	def loadObject(self):
		self.removeObject()
		self.jar = loader.loadModel("phase_5.5/models/estate/jellybeanJar.bam")
		self.jar.setZ(1.0)
		self.jar.setTwoSided(1)
		self.jar.reparentTo(self)

	def removeObject(self):
		if self.jar:
			self.jar.removeNode()
			self.jar = None

	def handleCollisions(self, entry):
		SoundInterval(self.tickSfx, startTime = 0.05, volume = 2.0).start()
		DistributedDroppableCollectableJellybeans.handleCollisions(self, entry)

	def load(self):
		self.tickSfx = base.loadSfx("phase_4/audio/sfx/MG_maze_pickup.mp3")
		self.collectSfx = base.loadSfx("phase_4/audio/sfx/MG_pos_buzzer.wav")
		DistributedDroppableCollectableJellybeans.load(self)

	def unload(self):
		self.tickSfx = None
		DistributedDroppableCollectableJellybeans.unload(self)

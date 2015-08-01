"""

  Filename: DistributedDroppableCollectableJellybeans.py
  Created by: blach (22Mar15)
  
"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import *
from DistributedDroppableCollectableObject import DistributedDroppableCollectableObject

class DistributedDroppableCollectableJellybeans(DistributedDroppableCollectableObject):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeans")
	
	def __init__(self, cr):
		DistributedDroppableCollectableObject.__init__(self, cr)
		
	def handleCollisions(self, entry):
		SoundInterval(self.collectSfx).start()
		DistributedDroppableCollectableObject.handleCollisions(self, entry)
		
	def unload(self):
		self.collectSfx = None
		DistributedDroppableCollectableObject.unload(self)

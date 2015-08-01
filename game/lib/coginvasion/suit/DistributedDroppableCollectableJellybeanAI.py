"""

  Filename: DistributedDroppableCollectableJellybeanAI.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableJellybeansAI import DistributedDroppableCollectableJellybeansAI

class DistributedDroppableCollectableJellybeanAI(DistributedDroppableCollectableJellybeansAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeanAI")
	
	def __init__(self, air):
		DistributedDroppableCollectableJellybeansAI.__init__(self, air)

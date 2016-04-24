# Filename: DistributedDodgeballGameAI.py
# Created by:  blach (18Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedToonFPSGameAI import DistributedToonFPSGameAI

class DistributedDodgeballGameAI(DistributedToonFPSGameAI):
    """The winter dodgeball game (AI/server side)"""
    
    notify = directNotify.newCategory("DistributedDodgeballGameAI")



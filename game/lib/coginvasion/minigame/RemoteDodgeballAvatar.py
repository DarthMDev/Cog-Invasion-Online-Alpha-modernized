# Filename: RemoteDodgeballAvatar.py
# Created by:  blach (30Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify

from RemoteAvatar import RemoteAvatar
from DistributedDodgeballGame import TEAM_COLOR_BY_ID

class RemoteDodgeballAvatar(RemoteAvatar):
    """A wrapper around a remote DistributedToon for use in the Dodgeball minigame (client side)"""

    notify = directNotify.newCategory("RemoteDodgeballAvatar")

    def __init__(self, mg, cr, avId):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.retrieveAvatar()

    def setTeam(self, team):
        RemoteAvatar.setTeam(self, team)
        self.teamText.node().setText(self.mg.teamNameById[team])
        self.teamText.node().setTextColor(TEAM_COLOR_BY_ID[team])



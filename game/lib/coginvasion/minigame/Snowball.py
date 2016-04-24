# Filename: Snowball.py
# Created by:  blach (19Apr16)

from panda3d.core import NodePath, CollisionNode, CollisionSphere

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals

class Snowball(NodePath):
    """Represents a useable snowball in Winter Dodgeball minigame (client)"""

    notify = directNotify.newCategory("Snowball")

    def __init__(self, mg):
        # The minigame
        self.mg = mg

        # The snowball geometry
        self.model = None
        self.collNP = None

        # Has the snowball been thrown and is it currently in the air?
        self.isAirborne = False

        # The avatar that is currently holding this snowball.
        self.owner = None

        NodePath.__init__(self, "snowball")

    def load(self):
        self.model = loader.loadModel("phase_5/models/props/snowball.bam")
        self.model.reparentTo(self)

        # Setup collisions
        sphere = CollisionSphere(0, 0, 0, 1)
        sphere.setTangible(0)
        node = CollisionNode('snowball-coll-' + str(id(self)))
        node.addSolid(sphere)
        node.setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)
        self.collNP = self.attachNewNode(node)
        self.collNP.setCollideMask(BitMask32(0))

    def setOwner(self, owner):
        """
        Sets the owner of this snowball.
        owner - A DodgeballRemoteAvatar instance
        """
        self.owner = owner

    def getOwner(self):
        return self.owner

    def hasOwner(self):
        """Returns whether or not this snowball has an owner."""
        return self.owner is not None



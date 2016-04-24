# Filename: DodgeballFirstPerson.py
# Created by:  blach (18Apr16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.actor.Actor import Actor

from FirstPerson import FirstPerson
from MinigameUtils import *

class DodgeballFirstPerson(FirstPerson):
    """The first person controls for the local player in Winter Dodgeball"""

    notify = directNotify.newCategory("DodgeballFirstPerson")

    def __init__(self, mg):
        self.mg = mg
        self.crosshair = None
        self.soundCatch = None
        self.vModelRoot = None
        self.vModel = None
        self.fsm = ClassicFSM.ClassicFSM("DodgeballFirstPerson",
                                         [State.State("off", self.enterOff, self.exitOff),
                                          State.State("hold", self.enterHold, self.exitHold),
                                          State.State("catch", self.enterCatch, self.exitCatch),
                                          State.State("throw", self.enterThrow, self.exitThrow)],
                                         "off", "off")
        self.fsm.enterInitialState()

        FirstPerson.__init__(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterHold(self):
        self.vModel.loop("hold")

    def exitHold(self):
        self.vModel.stop()

    def enterThrow(self):
        self.vModel.play("throw")

    def exitThrow(self):
        self.vModel.stop()

    def enterCatch(self):
        self.vModel.play("")

    def start(self):
        # Black crosshair because basically the entire arena is white.
        self.crosshair = getCrosshair(color = (0, 0, 0, 1))

        self.soundCatch = base.loadSfx("phase_4/audio/sfx/MG_sfx_vine_game_catch.mp3")

        self.vModelRoot = camera.attachNewNode('vModelRoot')
        self.vModelRoot.setPos(-0.09, 1.38, -2.48)

        self.vModel = Actor("phase_4/models/minigames/v_dgm.egg",
                            {"hold": "phase_4/models/minigames/v_dgm-ball-hold.egg",
                             "hold-start": "phase_4/models/minigames/v_dgm-ball-hold-start.egg",
                             "throw": "phase_4/models/minigames/v_dgm-ball-throw.egg",
                             "catch": "phase_4/models/minigamse/v_dgm-ball-catch.egg"})
        self.vModel.reparentTo(self.vModelRoot)

        FirstPerson.start(self)




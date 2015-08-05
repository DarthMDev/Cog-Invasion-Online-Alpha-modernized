# Filename: NameTag.py
# Created by:  blach (??Jul14)


from direct.gui.DirectGui import OnscreenText
from direct.fsm import ClassicFSM, State

from lib.coginvasion.globals import CIGlobals

class NameTag(OnscreenText):
    NameTagColors = {CIGlobals.Suit: {"fg": (0.2, 0.2, 0.2, 1.0),
                            "bg": (0.8, 0.8, 0.8, 0.5)},
                    CIGlobals.Toon: {"fg": (0.8, 0.4, 0.0, 1.0),
                            "bg": (0.8, 0.8, 0.8, 0.5)},
                    CIGlobals.CChar: {"fg": (0.2, 0.5, 0.0, 1.0),
                            "bg": (0.8, 0.8, 0.8, 0.5)}}
    NameTagBackgrounds = {'rollover': (1.0, 1.0, 1.0, 0.65),
        'down': (0.3, 0.3, 0.3, 0.5),
        'up': (0.8, 0.8, 0.8, 0.5)}
    LocalNameTagColor = (0.3, 0.3, 0.7, 1.0)

    def __init__(self, name, avatarType):
        self.avatarType = avatarType
        self.fsm = ClassicFSM.ClassicFSM('NameTag', [State.State('off', self.enterOff, self.exitOff),
            State.State('rollover', self.enterRollover, self.exitRollover),
            State.State('down', self.enterDown, self.exitDown),
            State.State('up', self.enterUp, self.exitUp)],
            'off', 'off')
        self.fsm.enterInitialState()
        OnscreenText.__init__(self, text = name, fg = (0.191406, 0.5625, 0.773438, 1.0),
            wordwrap = 8, decal = True, parent = hidden)
        self.setBillboardPointEye()
        self.clickable = 0

    def setColorLocal(self):
        self['fg'] = self.LocalNameTagColor

    def setClickable(self, value):
        self.clickable = value

    def getClickable(self):
        return self.clickable

    def setPickerState(self, state):
        self.fsm.request(state)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterRollover(self):
        self['bg'] = self.NameTagBackgrounds['rollover']

    def exitRollover(self):
        pass

    def enterDown(self):
        self['bg'] = self.NameTagBackgrounds['down']

    def makeDefaultFG(self):
        self['fg'] = self.NameTagColors[self.avatarType]["fg"]

    def exitDown(self):
        pass

    def enterUp(self):
        self['bg'] = self.NameTagBackgrounds['up']

    def exitUp(self):
        pass

    def destroy(self):
        self.fsm.requestFinalState()
        del self.fsm
        del self.avatarType
        del self.clickable
        OnscreenText.destroy(self)

########################################
# Filename: NamePage.py
# Created by: DecodedLogic (12Apr16)
########################################

from direct.fsm.StateData import StateData
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

from lib.coginvasion.globals import CIGlobals
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import TextNode
import math

class NamePage(StateData):
    notify = directNotify.newCategory('NamePage')
    
    def __init__(self, book, parentFSM):
        self.book = book
        self.parentFSM = parentFSM
        StateData.__init__(self, 'namePageDone')
        self.fsm = ClassicFSM('NamePage', [State('off', self.enterOff, self.exitOff),
            State('basePage', self.enterBasePage, self.exitBasePage)], 
        'off', 'off')
        self.fsm.enterInitialState()
        self.parentFSM.getStateNamed('namePage').addChild(self.fsm)
        self.nameServ = base.cr.nameServicesManager
        self.baseRequestIndex = 0
        self.requestsPerCluster = 4
        
        # GUI elements
        self.requestsContainer = {}
        self.loadingLabel = None
        
    def handleRequests(self):
        self.loadingLabel.hide()
        for i in xrange(self.requestsPerCluster):
            request = self.nameServ.getNameRequests()[self.baseRequestIndex + i]
            date = request['date']
            date = date.replace(' ', '-')
            posY = 0.5 - (i * 0.1)
            
            nameLabel = OnscreenText(text = request['name'], font = CIGlobals.getToonFont(), 
                pos = (-0.75, posY, 0), scale = 0.04, align = TextNode.ALeft, parent = aspect2d)
            
            date = OnscreenText(text = date, font = CIGlobals.getToonFont(),
                pos = (-0.15 + (math.ceil((len(request['name']) - 12) / 12) * 0.2), posY, 0), scale = 0.04, parent = aspect2d)
            
            geom = CIGlobals.getDefaultBtnGeom()
            acceptBtn = DirectButton(
                geom = geom,
                text_scale = 0.04,
                relief = None,
                scale = 0.5,
                text = "Accept",
                pos = (0.5, posY, 0),
                text_pos = (0, -0.01),
                command = self.enterOff,
            )
            declineBtn = DirectButton(
                geom = geom,
                text_scale = 0.04,
                relief = None,
                scale = 0.5,
                text = "Decline",
                pos = (0.75, posY, 0),
                text_pos = (0, -0.01),
                command = self.enterOff,
            )
            elements = [nameLabel, date, acceptBtn, declineBtn]
            self.requestsContainer.update({int(self.baseRequestIndex + i) : elements})
            
    
    def load(self):
        StateData.load(self)
        self.loadingLabel = OnscreenText(text = 'Loading...', 
            font = CIGlobals.getToonFont(), pos = (0, 0.1, 0), scale = 0.08, parent = aspect2d)
        
    def unload(self):
        StateData.unload(self)
        self.loadingLabel.destroy()
        self.loadingLabel = None
        for request in self.requestsContainer.values():
            for element in request:
                element.destroy()
        self.requestsContainer = {}
        
    def enter(self):
        StateData.enter(self)
        self.fsm.request('basePage')
        base.acceptOnce(self.nameServ.getRequestCompleteName(), self.handleRequests)
        self.nameServ.d_requestNameData()
        
    def exit(self):
        self.fsm.requestFinalState()
        StateData.exit(self)
        
    def enterBasePage(self):
        self.book.createPageButtons('adminPage', None)
        self.book.setTitle('Name Approval')
        
    def exitBasePage(self):
        self.book.deletePageButtons(True, False)
        self.book.clearTitle()
        
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
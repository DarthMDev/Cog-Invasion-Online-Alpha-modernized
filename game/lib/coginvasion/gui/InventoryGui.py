########################################
# Filename: InventoryGui.py
# Created by: DecodedLogic (12Jul15)
########################################

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import DirectFrame, OnscreenImage, DirectLabel, OnscreenText, DGG
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectWaitBar import DirectWaitBar

from direct.interval.IntervalGlobal import Sequence, Wait, Func

from lib.coginvasion.gags.GagState import GagState
from lib.coginvasion.gags import GagGlobals

from panda3d.core import TransparencyAttrib, TextNode
import types

class Slot(DirectFrame):

    def __init__(self, baseGui, index, pos, parent):
        DirectFrame.__init__(self, pos = pos, parent = parent, image = loader.loadTexture('phase_3.5/maps/slot_%s_%s.png' % (str(index), 'idle')), scale = 0.15, 
            frameSize = (-1, 1, -1, 1), frameColor = (0, 0, 0, 0), sortOrder = 0)
        self.initialiseoptions(Slot)
        self.gui = baseGui
        self.index = index
        self.hoverObj = None
        self.gagImage = None
        self.gag = None
        self.mouseRlvrSfx = base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg')
        self.soundRecharged = base.loadSfx('phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.ogg')
        
        # The no ammo text over the gag when you run out of ammo.
        self.infoText = OnscreenText(text = "No\nAmmo", fg = (1, 0, 0, 1), parent = self,
                                       scale = 0.5, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, 0.1))
        self.infoText.setBin('unsorted', 100)
        self.infoText.hide()
        
        # The recharging progress bar.
        self.rechargeBar = DirectWaitBar(value = 0, range = 100, frameColor = (1, 1, 1, 1),
                                        barColor = (0.286, 0.901, 1, 1), relief = DGG.RAISED,
                                        borderWidth = (0.04, 0.04), pos = (-1.25, 0, 0),
                                        hpr = (0, 0, -90), parent = self, frameSize = (-0.85, 0.85, -0.12, 0.12))
        self.rechargeBar.setBin('fixed', 60)
        self.rechargeBar.hide()
        
        # The gag label underneath the gag icon.
        self.gagLabel = OnscreenText(text = "Birthday Cake", fg = (1, 1, 1, 1), parent = self,
                                       scale = 0.25, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, -0.9), mayChange = 1)
        self.gagLabel.setBin('fixed', 50)
        self.gagLabel.hide()
        
        # The left arrow for moving to the gag before this one in the sequence.
        battleGui = loader.loadModel('phase_3.5/models/gui/battle_gui.bam')
        arrow = battleGui.find('**/PckMn_BackBtn')
        arrowRlvr = battleGui.find('**/PckMn_BackBtn_Rlvr')
        arrowDn = battleGui.find('**/PckMn_BackBtn_Dn')
        self.leftArrow = DirectButton(geom = (arrow, arrowDn, arrowRlvr, arrow),
            parent = self, pos = (-0.925, -2.0, -1.02), relief = None, scale = 2,
            command = self.updateLoadout, extraArgs = [0], geom3_color = (0.5, 0.5, 0.5, 1.0))
        self.leftArrow.setBin('fixed', 60)
        self.rightArrow = DirectButton(geom = (arrow, arrowDn, arrowRlvr, arrow),
            parent = self, pos = (0.925, -2.0, -1.02), hpr = (180, 0, 0), relief = None, scale = 2,
            command = self.updateLoadout, extraArgs = [1], geom3_color = (0.5, 0.5, 0.5, 1.0))
        self.rightArrow.setBin('fixed', 60)
        
        self.hoverObj = DirectButton(relief = None, parent = self, frameSize = self['frameSize'])
        
        self.setBin('transparent', 30)
        self.setOutlineImage('idle')
        
        # Let's handle mouse entering and leaving.
        self.hoverObj.guiItem.setActive(True)
        self.hoverObj.bind(DGG.WITHIN, self.mouseEntered)
        self.hoverObj.bind(DGG.WITHOUT, self.mouseExited)
        self.hoverObj.bind(DGG.B1CLICK, self.gui.click_setWeapon, [self])

    def toggleArrows(self, left, right):
        if left:
            self.leftArrow['state'] = DGG.NORMAL
        else:
            self.leftArrow['state'] = DGG.DISABLED

        if right:
            self.rightArrow['state'] = DGG.NORMAL
        else:
            self.rightArrow['state'] = DGG.DISABLED
        
    def updateArrows(self):
        if not self.gag:
            self.toggleArrows(False, False)
        else:
            track = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.getTrackOfGag(self.gag.getID()))
            index = None
            
            useTrack = []
            
            for name in track:
                gag = self.gui.backpack.getGagByID(GagGlobals.getIDByName(name))
                if gag == self.gag or (not gag in self.gui.backpack.getLoadout()):
                    useTrack.append(name)
                    
            index = useTrack.index(self.gag.getName())
            
            if index == 0:
                self.toggleArrows(False, True)

            elif(index > 0 and index < (len(useTrack) - 1)):
                gagId = GagGlobals.getIDByName(useTrack[index + 1])
                if not self.gui.backpack.hasGag(gagId):
                    self.toggleArrows(True, False)

            elif(index == (len(useTrack) - 1)):
                self.toggleArrows(True, False)

            else:
                self.toggleArrows(True, True)
        
    def updateLoadout(self, forward):
        if self.gag and self.gag.getState() in [GagState.RECHARGING, GagState.LOADED]:
            track = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.getTrackOfGag(self.gag.getID()))
            index = None
            
            useTrack = []
            
            for name in track:
                gag = self.gui.backpack.getGagByID(GagGlobals.getIDByName(name))
                if gag == self.gag or (not gag in self.gui.backpack.getLoadout()):
                    useTrack.append(name)
                    
            index = useTrack.index(self.gag.getName())
            
            if forward == 1:
                nextGagIndex = index + 1
            else:
                nextGagIndex = index - 1
                
            if nextGagIndex < 0 or nextGagIndex >= len(useTrack):
                return
            
            gagId = GagGlobals.getIDByName(useTrack[nextGagIndex])
            loadout = self.gui.backpack.getLoadout()
            if self.gui.backpack.hasGag(gagId) and self.gag in loadout:
                self.hideInfoText()
                
                if not self.gag in loadout:
                    return

                loadout[loadout.index(self.gag)] = self.gui.backpack.getGagByID(gagId)
                self.gui.backpack.setLoadout(loadout)
        
    def showNoAmmo(self):
        self.infoText['text'] = "No\nAmmo"
        self.infoText['scale'] = 0.5
        self.infoText['fg'] = (1, 0, 0, 1)
        self.infoText['pos'] = (0, 0.1)
        self.infoText.show()
        
        if self.gag and self.gag.getState() == GagState.RECHARGING:
            self.rechargeBar.show()
        
    def showRecharging(self):
        self.infoText['text'] = "Recharging..."
        self.infoText['scale'] = 0.315
        self.infoText['fg'] = (0.286, 0.901, 1, 1)
        self.infoText['pos'] = (0, 0)
        self.infoText.show()
        
        self.rechargeBar.show()
        
    def __tickRecharge(self):
        if not self.gag:
            self.ignoreAll()
        else:
            elapsedTime = float(self.gag.getRechargeElapsedTime())
            totalTime = float(self.gag.getRechargeTime())
            barValue = int(float(elapsedTime / totalTime) * self.rechargeBar['range'])
            self.rechargeBar['value'] = barValue
            
            if barValue == 0:
                self.gui.setWeapon(self, playSound = False)
                self.setOutlineImage('no_ammo')
                self.showRecharging()
            elif barValue >= 100:
                base.playSfx(self.soundRecharged)
                slotImage = 'idle'
                if base.localAvatar.getBackpack().getSupply(self.gag.getID()) <= 0:
                    slotImage = 'no_ammo'
                Sequence(Wait(0.5), Func(self.setOutlineImage, slotImage)).start()
        
    def hideInfoText(self):
        self.infoText.hide()
        self.rechargeBar.hide()

    def setSlotImage(self, gagImage):
        if self.gagImage:
            self.gagImage.destroy()
            self.gagImage = None
        self.gagImage = OnscreenImage(image = gagImage, parent = self)
        self.gagImage.setTransparency(TransparencyAttrib.MAlpha)

    def setOutline(self):
        self.setTransparency(TransparencyAttrib.MAlpha)

    def setOutlineImage(self, image):
        phase = 'phase_3.5/maps/'
        self['image'] = loader.loadTexture(phase + 'slot_%s_%s.png' % (str(self.index), image))
        self.setOutline()
        
        if image != 'no_ammo':
            if self.gag and base.localAvatar.getBackpack().getSupply(self.gag.getID()) == 0 or self.gag and self.gag.getState() == GagState.RECHARGING:
                image = 'no_ammo'
        
        if image == 'no_ammo':
            if self.gag and self.gag.getState() == GagState.RECHARGING:
                # Show the recharge text.
                self.showRecharging()
            else:
                # Show the no ammo text.
                self.showNoAmmo()
                self.rechargeBar.hide()
            # When we have no ammo, render the frame in front of the gag image.
            self.setBin('fixed', 40)
            
            if self.gagImage:
                self.gagImage.setBin('transparent', 30)
        else:
            # Hide the no ammo text if we're not out of ammo.
            self.hideInfoText()
            # Render the gag image in front of the frame.
            if self.gagImage:
                self.gagImage.setBin('fixed', 40)
            self.setBin('transparent', 30)

    def getOutline(self):
        return self.outline
    
    def mouseEntered(self, cmd):
        if self.gag:
            self.gagLabel.show()
            self.mouseRlvrSfx.play()
            
    def mouseExited(self, cmd):
        self.gagLabel.hide()

    def setGag(self, gag):
        if type(gag) == types.IntType:
            gag = self.gui.backpack.getGagByID(gag)
        self.ignoreAll()
        self.gag = gag
        if gag:
            self.show()
            self.setSlotImage(self.gag.getImage())
            self.gagLabel['text'] = self.gag.getName()
            self.accept('%s-Recharge-Tick' % (str(self.gag.getID())), self.__tickRecharge)
        else:
            self.hide()
            self.gagLabel['text'] = ''
        self.updateArrows()

    def getGag(self):
        return self.gag

class InventoryGui(DirectObject):
    directNotify = DirectNotify().newCategory('InventoryGui')

    def __init__(self):
        DirectObject.__init__(self)
        self.backpack = base.localAvatar.backpack
        self.backpack.loadoutGUI = self
        
        self.oneSlotPos = [(0, 0, 0)]
        self.twoSlotsPos = [(0, 0, 0.30), (0, 0, -0.2)]
        self.threeSlotsPos = [(0, 0, 0.5), (0, 0, 0), (0, 0, -0.5)]
        self.fourSlotPos = [(0, 0, 0.5), (0, 0, 0.15), (0, 0, -0.2), (0, 0, -0.55)]
        self.availableSlot = 0
        self.slots = []
        self.activeSlot = None
        self.defaultSlots = 3
        self.prevSlot = None
        self.ammoLabel = None
        self.inventoryFrame = None
        self.switchSound = True
        self.switchSoundSfx = base.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.ogg")
        
    def click_setWeapon(self, slot, cmd):
        self.setWeapon(slot, playSound = False)

    def setWeapon(self, slot, playSound = True):
        if isinstance(slot, str):
            for iSlot in self.slots:
                if iSlot.getGag():
                    if iSlot.getGag().getID() == slot:
                        slot = iSlot
        if self.activeSlot:
            self.activeSlot.setOutlineImage('idle')
            self.prevSlot = self.activeSlot
        if slot.getGag() and self.backpack.getSupply(slot.getGag().getID()) > 0 and not slot.getGag().getState() == GagState.RECHARGING:
            if self.activeSlot != slot:
                gagId = slot.getGag().getID()
                # We need to wait until our current gag has finished its time
                # out in order to equip the new gag.
                base.localAvatar.needsToSwitchToGag = gagId
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_equip(gagId)
                    base.localAvatar.enableGagKeys()
                slot.setOutlineImage('selected')
                self.activeSlot = slot
            elif self.activeSlot == slot and slot.getGag().getState() in [GagState.LOADED, GagState.RECHARGING]:
                base.localAvatar.needsToSwitchToGag = 'unequip'
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_unEquip()
                    base.localAvatar.enableGagKeys()
                self.activeSlot = None
            self.update()
            if self.switchSound and playSound:
                base.playSfx(self.switchSoundSfx)

    def createGui(self):
        self.deleteGui()
        posGroup = self.threeSlotsPos
        self.inventoryFrame = DirectFrame(parent = base.a2dRightCenter, pos = (-0.1725, 0, 0))
        if self.defaultSlots == 4:
            posGroup = self.fourSlotPos
        for slot in range(len(posGroup) + 1):
            if slot == 3:
                posGroup = self.fourSlotPos
            slotObj = Slot(self, slot + 1, posGroup[slot], self.inventoryFrame)
            self.slots.append(slotObj)
            if slot == 3:
                slotObj.hide()
        self.ammoLabel = DirectLabel(text = "Ammo: 0", text_fg=(1,1,1,1), relief=None, text_shadow=(0,0,0,1), text_scale=0.08, pos=(0.2, 0, 0.35), parent=base.a2dBottomLeft)
        self.ammoLabel.hide()
        self.enableWeaponSwitch()
        self.resetScroll()
        self.update()

    def deleteGui(self):
        self.disableWeaponSwitch()
        for slot in self.slots:
            slot.destroy()
        self.slots = []
        if self.ammoLabel:
            self.ammoLabel.destroy()
            self.ammoLabel = None
        if self.inventoryFrame:
            self.inventoryFrame.destroy()
            self.inventoryFrame = None

    def resetScroll(self):
        nextGag = 0
        prevGag = -1
        curGag = -1
        if self.prevSlot:
            prevGag = self.slots.index(self.prevSlot)
        if self.activeSlot:
            curGag = self.slots.index(self.activeSlot)
        if curGag == (len(self.slots) - 1):
            nextGag = 0
            prevGag = curGag - 1
        elif curGag == 0:
            nextGag = 1
            prevGag = (len(self.slots) - 1)
        elif curGag == -1:
            prevGag = (len(self.slots) - 1)
        else:
            nextGag = curGag + 1
            prevGag = curGag - 1
        self.accept('wheel_down', self.setWeapon, extraArgs = [self.slots[nextGag]])
        self.accept('wheel_up', self.setWeapon, extraArgs = [self.slots[prevGag]])

    def update(self):
        if not self.backpack: return
        for element in [self.ammoLabel, self.inventoryFrame]:
            if not element: return
        updateSlots = list(self.slots)
        for slot in self.slots:
            gag = slot.getGag()
            if not gag:
                updateSlots.remove(slot)
                slot.hide()
                continue
            supply = self.backpack.getSupply(gag.getID())
            index = self.slots.index(slot)
            if not gag and len(self.backpack.getGags()) - 1 >= index:
                gag = self.backpack.getGagByIndex(index)
                slot.setGag(gag)
                if self.backpack.getSupply(gag.getID()) > 0 and not gag.getState() == GagState.RECHARGING:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')
            else:
                if slot == self.activeSlot:
                    self.ammoLabel['text_fg'] = (1, 1, 1, 1)
                    if supply > 0 and not gag.getState() == GagState.RECHARGING:
                        slot.setOutlineImage('selected')
                    else:
                        if supply <= 0:
                            self.ammoLabel['text_fg'] = (0.9, 0, 0, 1)
                        slot.setOutlineImage('no_ammo')
                        self.activeSlot = None
                    self.ammoLabel.show()
                    self.ammoLabel['text'] = 'Ammo: %s' % (self.backpack.getSupply(slot.getGag().getID()))
                elif self.backpack.getSupply(slot.getGag().getID()) > 0 and not gag.getState() == GagState.RECHARGING:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')
        
        numSlots = len(updateSlots)
        posGroup = {1 : self.oneSlotPos, 2 : self.twoSlotsPos, 3 : self.threeSlotsPos, 4 : self.fourSlotPos}.get(numSlots)
        
        for i in xrange(len(updateSlots)):
            updateSlots[i].setPos(posGroup[i])
            updateSlots[i].show()
        
        if self.activeSlot == None:
            self.ammoLabel.hide()
            self.ammoLabel['text'] = 'Ammo: 0'
        self.resetScroll()

    def setBackpack(self, backpack):
        self.backpack = backpack

    def updateLoadout(self):
        if self.backpack:
            loadout = self.backpack.getLoadout()
            if len(loadout) <= 3:
                self.reseatSlots()
            elif len(loadout) == 4:
                self.reseatSlots(slots = 4)
            for i in range(len(self.slots)):
                slot = self.slots[i]
                if i < len(loadout):
                    slot.setGag(loadout[i])
                else:
                    slot.setGag(None)
            self.update()

    def reseatSlots(self, slots = 3):
        for slot in range(len(self.slots) - 1):
            if slots == 4:
                self.slots[slot].setPos(self.fourSlotPos[slot])
            else: self.slots[slot].setPos(self.threeSlotsPos[slot])

    def enableWeaponSwitch(self):
        for index in range(len(self.slots)):
            self.accept(str(index + 1), self.setWeapon, extraArgs = [self.slots[index]])

    def disableWeaponSwitch(self):
        for key in ['1', '2', '3', '4', 'wheel_down', 'wheel_up']:
            self.ignore(key)

    def getSlots(self):
        return self.slots

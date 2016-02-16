"""

  Filename: InventoryGui.py
  Created by: DecodedLogic (12Jul15)

"""

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import DirectFrame, OnscreenImage, DirectLabel, OnscreenText, DGG
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.gags.GagState import GagState
from panda3d.core import TransparencyAttrib, TextNode
from direct.gui.DirectButton import DirectButton

class Slot(DirectFrame):

    def __init__(self, index, pos, parent):
        DirectFrame.__init__(self, pos = pos, parent = parent, image = loader.loadTexture('phase_3.5/maps/slot_%s_%s.png' % (str(index), 'idle')), scale = 0.15, 
            frameSize = (-1, 1, -1, 1), frameColor = (0, 0, 0, 0.5), sortOrder = 0)
        self.index = index
        self.hoverObj = None
        self.gagImage = None
        self.gag = None
        self.mouseRlvrSfx = loader.loadSfx('phase_3/audio/sfx/GUI_rollover.mp3')
        
        # The no ammo text over the gag when you run out of ammo.
        self.noAmmoText = OnscreenText(text = "No\nAmmo", fg = (1, 0, 0, 1), parent = self,
                                       scale = 0.5, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, 0.1))
        self.noAmmoText.setBin('unsorted', 100)
        self.noAmmoText.hide()
        
        # The gag label underneath the gag icon.
        self.gagLabel = OnscreenText(text = "Birthday Cake", fg = (1, 1, 1, 1), parent = self,
                                       scale = 0.25, shadow = (0, 0, 0, 1), align = TextNode.ACenter,
                                       pos = (0, -0.9), mayChange = 1)
        self.gagLabel.setBin('fixed', 40)
        self.gagLabel.hide()
        
        self.hoverObj = DirectButton(relief = None, parent = self, frameSize = self['frameSize'])
        
        self.setBin('transparent', 30)
        self.setOutlineImage('idle')
        
        self['state'] = DGG.NORMAL
        
        # Let's handle mouse entering and leaving.
        self.hoverObj.guiItem.setActive(True)
        self.hoverObj.bind(DGG.WITHIN, self.mouseEntered)
        self.hoverObj.bind(DGG.WITHOUT, self.mouseExited)
        
    def showNoAmmo(self):
        self.noAmmoText.show()
        
    def hideNoAmmo(self):
        self.noAmmoText.hide()

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
        
        if image == 'no_ammo':
            # Show the no ammo text.
            self.showNoAmmo()
            # When we have no ammo, render the frame in front of the gag image.
            self.setBin('fixed', 40)
            
            if self.gagImage:
                self.gagImage.setBin('transparent', 30)
        else:
            # Hide the no ammo text if we're not out of ammo.
            self.hideNoAmmo()
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
        self.gag = gag
        if gag:
            self.show()
            self.setSlotImage(self.gag.getImage())
            self.gagLabel['text'] = self.gag.getName()
        else:
            self.hide()
            self.gagLabel['text'] = ''

    def getGag(self):
        return self.gag

class InventoryGui(DirectObject):
    directNotify = DirectNotify().newCategory('InventoryGui')

    def __init__(self):
        DirectObject.__init__(self)
        self.backpack = None
        self.oneSlotPos = [(0, 0, 0)]
        self.twoSlotsPos = [(0, 0, 0), (0, 0, -0.5)]
        self.threeSlotsPos = [(0, 0, 0.5), (0, 0, 0), (0, 0, -0.5)]
        self.fourSlotPos = [(0, 0, 0.45), (0, 0, 0.15), (0, 0, -0.15), (0, 0, -0.45)]
        self.availableSlot = 0
        self.slots = []
        self.activeSlot = None
        self.defaultSlots = 3
        self.prevSlot = None
        self.ammoLabel = None
        self.inventoryFrame = None
        self.switchSound = True
        self.switchSoundSfx = base.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.mp3")

    def setWeapon(self, slot, playSound = True):
        if isinstance(slot, str):
            for iSlot in self.slots:
                if iSlot.getGag():
                    if iSlot.getGag().getName() == slot:
                        slot = iSlot
        if self.activeSlot:
            self.activeSlot.setOutlineImage('idle')
            self.prevSlot = self.activeSlot
        if self.backpack.getSupply(slot.getGag().getName()) > 0:
            if self.activeSlot != slot:
                gagName = slot.getGag().getName()
                gagId = GagGlobals.getIDByName(gagName)
                # We need to wait until our current gag has finished its time
                # out in order to equip the new gag.
                base.localAvatar.needsToSwitchToGag = gagId
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_equip(gagId)
                    base.localAvatar.enablePieKeys()
                slot.setOutlineImage('selected')
                self.activeSlot = slot
            elif self.activeSlot == slot and slot.getGag().getState() == GagState.LOADED:
                base.localAvatar.needsToSwitchToGag = 'unequip'
                if base.localAvatar.gagsTimedOut == False:
                    base.localAvatar.b_unEquip()
                    base.localAvatar.enablePieKeys()
                self.activeSlot = None
            self.update()
            if self.switchSound and playSound:
                base.playSfx(self.switchSoundSfx)

    def createGui(self):
        self.deleteGui()
        posGroup = self.threeSlotsPos
        self.inventoryFrame = DirectFrame(parent = base.a2dRightCenter, pos = (-0.2, 0, 0))
        if self.defaultSlots == 4:
            posGroup = self.fourSlotPos
        for slot in range(len(posGroup) + 1):
            if slot == 3:
                posGroup = self.fourSlotPos
            slotObj = Slot(slot + 1, posGroup[slot], self.inventoryFrame)
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
            self.slots.remove(slot)
            slot.destroy()
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
        for slot in self.slots:
            gag = slot.getGag()
            if not gag:
                continue
            supply = self.backpack.getSupply(gag.getName())
            index = self.slots.index(slot)
            if not gag and len(self.backpack.getGags()) - 1 >= index:
                gag = self.backpack.getGagByIndex(index)
                slot.setGag(gag)
                if self.backpack.getSupply(gag.getName()) > 0:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')
            else:
                if slot == self.activeSlot:
                    if supply > 0:
                        slot.setOutlineImage('selected')
                        self.ammoLabel['text_fg'] = (1, 1, 1, 1)
                    else:
                        slot.setOutlineImage('no_ammo')
                        self.ammoLabel['text_fg'] = (0.9, 0, 0, 1)
                        self.activeSlot = None
                    self.ammoLabel.show()
                    self.ammoLabel['text'] = 'Ammo: %s' % (self.backpack.getSupply(slot.getGag().getName()))
                elif self.backpack.getSupply(slot.getGag().getName()) > 0:
                    slot.setOutlineImage('idle')
                else:
                    slot.setOutlineImage('no_ammo')
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

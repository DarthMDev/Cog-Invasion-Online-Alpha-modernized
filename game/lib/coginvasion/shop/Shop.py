"""

  Filename: Shop.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, OnscreenImage, DGG
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.shop.ItemType import ItemType
from panda3d.core import Vec4, TransparencyAttrib
from direct.task.Task import Task

GRAYED_OUT_COLOR = Vec4(0.25, 0.25, 0.25, 1)
NORMAL_COLOR = Vec4(1, 1, 1, 1)

class Shop(StateData):
    notify = directNotify.newCategory('Shop')

    def __init__(self, distShop, doneEvent):
        StateData.__init__(self, doneEvent)
        self.distShop = distShop
        self.destroyEvent = self.distShop.destroyEvent
        self.origHealth = base.localAvatar.getHealth()
        self.avMoney = base.localAvatar.getMoney()
        self.healCooldownDoneSoundPath = 'phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.mp3'
        self.healCooldownDoneSfx = None
        self.newHealth = None
        self.pages = 1
        self.window = None
        self.upgradesPurchased = False
        
        # This handles heal cooldowns.
        self.healCooldowns = {}
        self.newHealCooldowns = {}
        self.acceptOnce(self.destroyEvent, self.destroy)

    def confirmPurchase(self):
        if self.newHealth != None:
            self.distShop.d_requestHealth(base.localAvatar.getHealth() - self.origHealth)
        messenger.send(self.doneEvent)

    def cancelPurchase(self):
        messenger.send(self.doneEvent)
        base.localAvatar.setMoney(self.avMoney)
        base.localAvatar.setHealth(self.origHealth)
        
        for healCooldown in self.newHealCooldowns.keys():
            del self.healCooldowns[healCooldown]
        
    def __purchaseUpgradeItem(self, values):
        upgradeID = values.get('upgradeID')
        upgrades = base.localAvatar.getPUInventory()[0]
        maxUpgrades = values.get('maxUpgrades')
        if upgrades < maxUpgrades:
            if upgrades < 0:
                upgrades = 1
            else:
                upgrades += 1
            self.upgradesPurchased = True
            base.localAvatar.getMyBattle().getTurretManager().setGag(upgradeID)
            base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))
            base.localAvatar.setPUInventory([upgrades, upgradeID])
            
    def __purchaseGagItem(self, gag, values):
        name = gag.getName()
        supply = self.backpack.getSupply(name)
        maxSupply = self.backpack.getMaxSupply(name)
        if supply < maxSupply:
            gagIds = []
            ammoList = []
            for bpGag in self.backpack.getGags():
                gagIds.append(bpGag.getID())
                bpSupply = self.backpack.getSupply(bpGag.getName())
                if bpGag.getName() == name:
                    if bpSupply < self.backpack.getMaxSupply(bpGag.getName()):
                        ammoList.append(supply + 1)
                        base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))
                        self.window.showInfo('Purchased a %s' % (name), duration = 3)
                else: ammoList.append(bpSupply)
            base.localAvatar.setBackpackAmmo(gagIds, ammoList)
            base.localAvatar.updateBackpackAmmo()
            
    def __purchaseHealItem(self, item, values):
        health = base.localAvatar.getHealth()
        maxHealth = base.localAvatar.getMaxHealth()
        healAmt = health + values.get('heal')
        if health < maxHealth and not self.hasCooldown(item):
            if healAmt > maxHealth:
                healAmt = maxHealth
            self.newHealth = healAmt
            base.localAvatar.setHealth(healAmt)
            healDict = {item : [0, values.get('healCooldown')]}
            self.healCooldowns.update(healDict)
            self.newHealCooldowns.update(healDict)
            base.taskMgr.doMethodLater(1, self.__doHealCooldown, item, extraArgs = [item], appendTask = True)
            base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))
            
    def __doHealCooldown(self, item, task):
        cooldownData = self.getCooldown(item)
        if cooldownData:
            cooldownTime = cooldownData[0]
            maxCooldownTime = cooldownData[1]
            cooldownTime += 1
            self.healCooldowns[item] = [cooldownTime, maxCooldownTime]
            if cooldownTime == maxCooldownTime:
                if item in self.healCooldowns:
                    del self.healCooldowns[item]
                if self.window:
                    self.healCooldownDoneSfx.play()
                self.update()
                return Task.done
            return Task.again
        return Task.done
        
    def getCooldown(self, item):
        if self.hasCooldown(item):
            return self.healCooldowns.get(item)
        
    def hasCooldown(self, item):
        return item in self.healCooldowns.keys()

    def purchaseItem(self, item):
        items = self.items
        itemType = None
        values = None
        for iItem, iValues in items.iteritems():
            if iItem == item:
                values = iValues
                itemType = values.get('type')
                break
        price = values.get('price')
        if self.isAffordable(price):
            if itemType == ItemType.GAG:
                self.__purchaseGagItem(item(), values)
            elif itemType == ItemType.UPGRADE:
                self.__purchaseUpgradeItem(values)
            elif itemType == ItemType.HEAL:
                self.__purchaseHealItem(item, values)
        self.update()

    def update(self):
        if self.window:
            self.window.updatePages()
            if base.localAvatar.getMoney() == 0: self.handleNoMoney()

    def handleNoMoney(self, duration = -1):
        self.window.showInfo('You need more jellybeans!', negative = 1, duration = duration)
        
    def isAffordable(self, price, silent = 0):
        if base.localAvatar.getMoney() - price >= 0:
            return True
        else:
            if not silent:
                Shop.handleNoMoney(self, duration = 2)
            return False

    def setup(self):
        pass

    def enter(self):
        StateData.enter(self)
        self.avMoney = base.localAvatar.getMoney()
        self.window = ShopWindow(self, image = 'phase_4/maps/FrameBlankA.jpg')
        self.window.setup()
        self.window.setOKCommand(self.confirmPurchase)
        self.window.setCancelCommand(self.cancelPurchase)
        self.window.makePages(self.distShop.getItems())
        self.window.setPage(0)
        
        # Load the rejection sfx.
        self.healCooldownDoneSfx = base.loadSfx(self.healCooldownDoneSoundPath)

    def exit(self):
        StateData.exit(self)
        if self.window: 
            self.window.delete()
            self.newHealth = None
            self.healCooldownDoneSfx = None
            
    def destroy(self):
        self.exit()
        for cooldown in self.healCooldowns.keys():
            base.taskMgr.removeTask(cooldown)
            if cooldown in self.healCooldowns:
                del self.healCooldowns[cooldown]

class Page(DirectFrame):

    def __init__(self, shop, window):
        DirectFrame.__init__(self, parent = window, sortOrder = 1)
        self.shop = shop
        self.itemEntries = {}
        self.items = {}

    def update(self):
        for item, values in self.items.iteritems():
            entry = self.itemEntries.get(item)
            itemType = values.get('type')
            price = values.get('price')
            money = base.localAvatar.getMoney()
            button = entry[0]
            label = entry[1]
            button.setColorScale(NORMAL_COLOR)
            if price > money:
                button.setColorScale(GRAYED_OUT_COLOR)
            if itemType == ItemType.GAG:
                name = item().getName()
                backpack = base.localAvatar.getBackpack()
                supply = backpack.getSupply(name)
                maxSupply = backpack.getMaxSupply(name)
                inBackpack = backpack.isInBackpack(name)
                if not inBackpack or inBackpack and supply >= maxSupply:
                    button.setColorScale(GRAYED_OUT_COLOR)
                supply = base.localAvatar.getBackpack().getSupply(name)
                maxSupply = base.localAvatar.getBackpack().getMaxSupply(name)
                label['text'] = '%s/%s\n%s JBS' % (str(supply), str(maxSupply), str(price))
            elif itemType == ItemType.UPGRADE:
                maxSupply = values.get('maxUpgrades')
                supply = base.localAvatar.getPUInventory()[0]
                if supply < 0:
                    supply = 0
                if supply >= maxSupply:
                    button.setColorScale(GRAYED_OUT_COLOR)
                label['text'] = '%s\n%s/%s\n%s JBS' % (item, str(supply), str(maxSupply), str(price))
            elif itemType == ItemType.HEAL:
                if base.localAvatar.getHealth() == base.localAvatar.getMaxHealth() or self.shop.hasCooldown(item):
                    button.setColorScale(GRAYED_OUT_COLOR)

    def addItemEntry(self, item, entry):
        self.itemEntries.update({item : entry})

    def addItem(self, item):
        self.items.update(item)

    def destroy(self):
        self.items = {}
        del self.items
        for key, entry in self.itemEntries.iteritems():
            entry[0].destroy()
            entry[1].destroy()
            self.itemEntries[key] = None
        DirectFrame.destroy(self)

class ShopWindow(DirectFrame):

    def __init__(self, shop, image):
        DirectFrame.__init__(self)
        self.shop = shop
        self.bgImage = image
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.nPage = -1
        self.nPages = 0
        self.nextPage = 0
        self.prevPage = -1
        self.pages = []
        self.isSetup = False

    def setup(self, title = 'CHOOSE WHAT YOU WANT TO BUY'):
        font = CIGlobals.getMickeyFont()
        txtFg = (0, 0, 0, 1)
        txtScale = 0.05
        txtPos = (0, -0.1)
        buttons = loader.loadModel('phase_3.5/models/gui/QT_buttons.bam')
        self.window = OnscreenImage(image = self.bgImage, scale = (0.9, 1, 0.7), parent = self)
        self.title = DirectLabel(text = title, relief = None, pos = (0, 0, 0.5), text_wordwrap = 10, text_font = font,
                                 text_fg = (1, 1, 0, 1), scale = 0.1, parent = self)
        self.infoLbl = DirectLabel(text = 'Welcome!', relief = None, text_scale = 0.075, text_fg = txtFg, text_shadow = (0, 0, 0, 0),
                                   pos = (0, 0, 0.215))
        self.okBtn = DirectButton(geom = CIGlobals.getOkayBtnGeom(), relief = None, text = 'OK', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (-0.1, 0, -0.5), parent = self)
        self.clBtn = DirectButton(geom = CIGlobals.getCancelBtnGeom(), relief = None, text = 'Cancel', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (0.1, 0, -0.5), parent = self)
        buttonGeom = (buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'))
        self.backBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (-0.3, 0, -0.25), parent = self, command = self.changePage, extraArgs = [0])
        self.nextBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (0.3, 0, -0.25), hpr = (0, 0, 180), command = self.changePage, extraArgs = [1], parent = self)
        self.hideInfo()

    def changePage(self, direction):
        var = self.prevPage
        if direction == 1:
            var = self.nextPage
        self.setPage(var)
        
    def __makeGagEntry(self, pos, item, values, page):
        itemImage = values.get('image')
        button = DirectButton(
                geom = (itemImage), scale = 1.3, pos = pos,
                relief = None, parent = page,
                command = self.shop.purchaseItem, extraArgs = [item]
        )
        supply = base.localAvatar.getBackpack().getSupply(item().getName())
        maxSupply = base.localAvatar.getBackpack().getMaxSupply(item().getName())
        buttonLabel = DirectLabel(
                text = '%s/%s\n%s JBS' % (str(supply), str(maxSupply),
                str(values.get('price'))), relief = None,
                parent = button, text_scale = 0.05, pos = (0, 0, -0.11)
        )
        self.addEntryToPage(page, item, values, button, buttonLabel)
        
    def __makeUpgradeEntry(self, pos, item, values, page):
        itemImage = values.get('image')
        button = DirectButton(
                image = (itemImage), scale = 0.15, pos = pos, relief = None,
                parent = page, command = self.shop.purchaseItem,
                extraArgs = [item]
        )
        button.setTransparency(TransparencyAttrib.MAlpha)
        upgradeID = values.get('upgradeID')
        supply = base.localAvatar.getPUInventory()[0]
        if supply < 0:
            supply = 0
        maxSupply = values.get('maxUpgrades')
        if upgradeID == 0 and base.localAvatar.getMyBattle().getTurretManager().myTurret:
            supply = 1
        buttonLabel = DirectLabel(
                 text = '%s\n%s/%s\n%s JBS' % (item, str(supply), str(maxSupply),
                 str(values.get('price'))), relief = None,
                 parent = button, text_scale = 0.3, pos = (0, 0, -1.2)
        )
        self.addEntryToPage(page, item, values, button, buttonLabel)
        
    def __makeHealEntry(self, pos, item, values, page):
        label = '%s' % (item)
        itemImage = values.get('image')
        if 'showTitle' in values:
            label = '%s\n%s JBS' % (item, values.get('price'))
        button = DirectButton(
                  image = (itemImage), scale = 0.105, pos = pos,
                  relief = None, parent = page,
                  command = self.shop.purchaseItem, extraArgs = [item]
        )
        button.setTransparency(TransparencyAttrib.MAlpha)
        buttonLabel = DirectLabel(
                  text = label, relief = None, parent = button,
                  text_scale = 0.55, pos = (0, 0, -1.6)
        )
        self.addEntryToPage(page, item, values, button, buttonLabel)
        
    def addEntryToPage(self, page, item, values, button, buttonLabel):
        page.addItemEntry(item, [button, buttonLabel])
        page.addItem({item : values})

    def makePages(self, items):
        newItems = dict(items)
        for item, values in newItems.items():
            if values.get('type') == ItemType.GAG:
                gag = item()
                if not base.localAvatar.getBackpack().isInBackpack(gag.getName()):
                    del newItems[item]
        self.nPages = int((len(newItems) / 4))
        if self.nPages % 4 != 0 and len(newItems) > 4:
            self.nPages += 1
        elif self.nPages == 0:
            self.nPages = 1
        itemPos = [(-0.45, 0, 0), (-0.15, 0, 0), (0.15, 0, 0), (0.45, 0, 0)]
        pageIndex = 0
        itemIndex = 0
        index = 1
        for _ in range(self.nPages):
            page = Page(self.shop, self)
            self.pages.append(page)
        for item, values in newItems.iteritems():
            pos = itemPos[itemIndex]
            page = self.pages[pageIndex]
            itemType = values.get('type')
            if itemType == ItemType.GAG:
                self.__makeGagEntry(pos, item, values, page)
            elif itemType == ItemType.UPGRADE:
                self.__makeUpgradeEntry(pos, item, values, page)
            elif itemType == ItemType.HEAL:
                self.__makeHealEntry(pos, item, values, page)
            if index % 4 == 0:
                index = 1
                pageIndex += 1
                itemIndex = 0
            else:
                itemIndex = itemIndex + 1
                index += 1
        if self.nPages == 1:
            self.backBtn.hide()
            self.nextBtn.hide()
        for page in self.pages:
            page.hide()
            page.update()
        self.isSetup = True

    def updatePages(self):
        for page in self.pages:
            page.update()

    def setPage(self, page):
        if self.nPage > -1:
            self.pages[self.nPage].hide()
        self.setBackBtn(True)
        self.setNextBtn(True)
        if (page - 1) < 0:
            self.setBackBtn(False)
        elif (page + 1) == self.nPages:
            self.setNextBtn(False)
        if page < 0 or page > self.nPages: return
        self.prevPage = (page - 1)
        self.nextPage = (page + 1)
        self.nPage = page
        self.pages[page].show()

    def setBackBtn(self, enabled):
        if self.backBtn:
            if enabled == False:
                self.backBtn.setColorScale(GRAYED_OUT_COLOR)
                self.backBtn['state'] = DGG.DISABLED
            else:
                self.backBtn.setColorScale(NORMAL_COLOR)
                self.backBtn['state'] = DGG.NORMAL

    def setNextBtn(self, enabled):
        if self.nextBtn:
            if enabled == False:
                self.nextBtn.setColorScale(GRAYED_OUT_COLOR)
                self.nextBtn['state'] = DGG.DISABLED
            else:
                self.nextBtn.setColorScale(NORMAL_COLOR)
                self.nextBtn['state'] = DGG.NORMAL

    def setOKCommand(self, command):
        if self.okBtn: self.okBtn['command'] = command

    def setCancelCommand(self, command):
        if self.clBtn: self.clBtn['command'] = command

    def showInfo(self, text, negative = 0, duration = -1):
        self.infoLbl.show()
        if negative:
            self.infoLbl['text_fg'] = (0.9, 0, 0, 1)
            self.infoLbl['text_shadow'] = (0, 0, 0, 1)
        else:
            self.infoLbl['text_fg'] = (0, 0, 0, 1)
            self.infoLbl['text_shadow'] = (0, 0, 0, 0)
        self.infoLbl['text'] = text
        if duration > -1: Sequence(Wait(duration), Func(self.hideInfo)).start()

    def hideInfo(self):
        if self.infoLbl: self.infoLbl.hide()

    def delete(self):
        elements = [self.title, self.okBtn, self.clBtn, self.infoLbl, self.backBtn, self.nextBtn]
        for element in elements:
            element.destroy()
        del elements
        for page in self.pages:
            page.destroy()
            self.pages.remove(page)
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.backBtn = None
        self.nextBtn = None
        self.bgImage = None
        if self.window:
            self.window.destroy()
            self.window = None
        self.destroy()

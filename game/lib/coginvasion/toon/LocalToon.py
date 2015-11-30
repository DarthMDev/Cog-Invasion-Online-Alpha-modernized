"""

  Filename: LocalToon.py
  Created by: blach (30Nov14)

"""

from panda3d.core import CollisionTraverser, Point3, CollisionRay, CollisionNode, BitMask32, CollisionHandlerQueue
from lib.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from direct.controls.GravityWalker import GravityWalker
from direct.task import Task
from DistributedToon import DistributedToon
from SmartCamera import SmartCamera
from lib.coginvasion.gui.ChatInput import ChatInput
from lib.coginvasion.gui.LaffOMeter import LaffOMeter
from lib.coginvasion.gui.MoneyGui import MoneyGui
from lib.coginvasion.gui.InventoryGui import InventoryGui
from lib.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.gui.DirectButton import DirectButton
from direct.showbase.InputStateGlobal import inputState
from direct.gui.DirectGui import DGG
from lib.coginvasion.hood import ZoneUtil
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.gui.ToonPanel import ToonPanel
from lib.coginvasion.friends.FriendRequestManager import FriendRequestManager
from lib.coginvasion.base.PositionExaminer import PositionExaminer
from lib.coginvasion.friends.FriendsList import FriendsList
from lib.coginvasion.suit import SuitAttacks

import random
from lib.coginvasion.gags.GagState import GagState

class LocalToon(DistributedToon):
    neverDisable = 1

    def __init__(self, cr):
        try:
            self.LocalToon_initialized
            return
        except:
            self.LocalToon_initialized = 1
        DistributedToon.__init__(self, cr)
        self.avatarChoice = cr.localAvChoice
        self.smartCamera = SmartCamera()
        self.chatInput = ChatInput()
        self.moneyGui = MoneyGui()
        self.laffMeter = LaffOMeter()
        self.positionExaminer = PositionExaminer()
        self.friendRequestManager = FriendRequestManager()
        self.friendsList = FriendsList()
        self.panel = ToonPanel()
        friendsgui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        self.friendButton = DirectButton(geom = (friendsgui.find('**/FriendsBox_Closed'),
            friendsgui.find('**/FriendsBox_Rollover'), friendsgui.find('**/FriendsBox_Rollover')),
            text = ("", "Friends", "Friends", ""),
            text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1), text_scale = 0.065,
            text_pos = (0, -0.2), relief = None, parent = base.a2dTopRight,
            pos = (-0.18, 0.0, -0.17), command = self.friendsButtonClicked, scale = 0.75)
        friendsgui.removeNode()
        del friendsgui
        self.hideFriendButton()
        self.runSfx = base.loadSfx("phase_3.5/audio/sfx/AV_footstep_runloop.wav")
        self.runSfx.setLoop(True)
        self.walkSfx = base.loadSfx("phase_3.5/audio/sfx/AV_footstep_walkloop.wav")
        self.walkSfx.setLoop(True)
        self.controlManager = ControlManager.ControlManager(True, False)
        self.offset = 3.2375
        self.movementKeymap = {
            "forward": 0, "backward": 0,
            "left": 0, "right": 0, "jump": 0
        }
        self.avatarMovementEnabled = False
        self.isMoving_forward = False
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_jump = False
        self.pieThrowBtn = None
        self.myBattle = None
        self.invGui = None

        self.pickerTrav = None
        self.pickerRay = None
        self.pickerRayNode = None
        self.pickerHandler = None
        self.rolledOverTag = None

        self.inTutorial = False
        self.hasDoneJump = False
        self.lastState = None
        self.lastAction = None
        
        self.__snowballButton = None
        #base.cTrav.showCollisions(render)

    def hasDiscoveredHood(self, zoneId):
        return zoneId in self.hoodsDiscovered

    def hasTeleportAccess(self, zoneId):
        return zoneId in self.teleportAccess

    def tutorialCreated(self, zoneId):
        self.cr.tutorialCreated(zoneId)

    def friendsButtonClicked(self):
        self.hideFriendButton()
        self.friendsList.fsm.request('onlineFriendsList')

    def hideFriendButton(self):
        self.friendButton.hide()

    def showFriendButton(self):
        self.friendButton.show()

    def gotoNode(self, node, eyeHeight = 3):
        possiblePoints = (Point3(3, 6, 0),
         Point3(-3, 6, 0),
         Point3(6, 6, 0),
         Point3(-6, 6, 0),
         Point3(3, 9, 0),
         Point3(-3, 9, 0),
         Point3(6, 9, 0),
         Point3(-6, 9, 0),
         Point3(9, 9, 0),
         Point3(-9, 9, 0),
         Point3(6, 0, 0),
         Point3(-6, 0, 0),
         Point3(6, 3, 0),
         Point3(-6, 3, 0),
         Point3(9, 9, 0),
         Point3(-9, 9, 0),
         Point3(0, 12, 0),
         Point3(3, 12, 0),
         Point3(-3, 12, 0),
         Point3(6, 12, 0),
         Point3(-6, 12, 0),
         Point3(9, 12, 0),
         Point3(-9, 12, 0),
         Point3(0, -6, 0),
         Point3(-3, -6, 0),
         Point3(0, -9, 0),
         Point3(-6, -9, 0))
        for point in possiblePoints:
            pos = self.positionExaminer.consider(node, point, eyeHeight)
            if pos:
                self.setPos(node, pos)
                self.lookAt(node)
                self.setHpr(self.getH() + random.choice((-10, 10)), 0, 0)
                return

        self.setPos(node, 0, 0, 0)

    def setFriendsList(self, friends):
        DistributedToon.setFriendsList(self, friends)
        self.cr.friendsManager.d_requestFriendsList()
        self.panel.maybeUpdateFriendButton()

    def d_requestAddFriend(self, avId):
        self.sendUpdate('requestAddFriend', [avId])

    def setupPicker(self):
        self.pickerTrav = CollisionTraverser('LT.pickerTrav')
        self.pickerRay = CollisionRay()
        rayNode = CollisionNode('LT.pickerNode')
        rayNode.addSolid(self.pickerRay)
        rayNode.setCollideMask(BitMask32(0))
        rayNode.setFromCollideMask(CIGlobals.WallBitmask)
        self.pickerRayNode = base.camera.attachNewNode(rayNode)
        self.pickerHandler = CollisionHandlerQueue()
        self.pickerTrav.addCollider(self.pickerRayNode, self.pickerHandler)

    def enablePicking(self):
        self.accept('mouse1', self.pickedSomething_down)
        self.accept('mouse1-up', self.pickedSomething_up)
        base.taskMgr.add(self.__travMousePicker, 'LT.travMousePicker')

    def disablePicking(self):
        base.taskMgr.remove('LT.travMousePicker')
        self.ignore('mouse1')
        self.ignore('mouse1-up')

    def pickedSomething_down(self):
        if self.rolledOverTag:
            base.playSfx(DGG.getDefaultClickSound())
            avatar = self.cr.doId2do.get(self.rolledOverTag)
            if avatar:
                avatar.nameTag.setPickerState('down')

    def pickedSomething_up(self):
        if self.rolledOverTag:
            avatar = self.cr.doId2do.get(self.rolledOverTag)
            if avatar:
                avatar.nameTag.setPickerState('up')
            self.panel.makePanel(self.rolledOverTag)

    def __travMousePicker(self, task):
        if not base.mouseWatcherNode.hasMouse():
            return task.cont

        mpos = base.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

        self.pickerTrav.traverse(render)
        if self.pickerHandler.getNumEntries() > 0:
            self.pickerHandler.sortEntries()
            pickedObject = self.pickerHandler.getEntry(0).getIntoNodePath()
            avatarId = pickedObject.getParent().getPythonTag('avatar')
            if avatarId != None:
                for do in self.cr.doId2do.values():
                    if do.__class__.__name__ == "DistributedToon":
                        if do.doId == avatarId:
                            if do.nameTag.getClickable() == 1:
                                if (do.nameTag.fsm.getCurrentState().getName() != "rollover" and
                                do.nameTag.fsm.getCurrentState().getName() != "down"):
                                    do.nameTag.setPickerState('rollover')
                                    base.playSfx(DGG.getDefaultRolloverSound())
                                    self.rolledOverTag = avatarId
                                    break
                                else:
                                    if (do.nameTag.fsm.getCurrentState().getName() == 'rollover'):
                                        if self.rolledOverTag != do.doId:
                                            do.nameTag.setPickerState('up')
                    else:
                        if do.__class__.__name__ == "DistributedToon":
                            if do.nameTag.fsm.getCurrentState().getName() != "up":
                                do.nameTag.setPickerState('up')
            else:
                if self.rolledOverTag:
                    avatar = self.cr.doId2do.get(self.rolledOverTag)
                    if avatar:
                        if avatar.nameTag.fsm.getCurrentState().getName() != "up":
                            avatar.nameTag.setPickerState('up')
                    self.rolledOverTag = None

        return task.cont
    
    def loadImageAsPlane(self, filepath, yresolution = 600):
        from panda3d.core import Texture, CardMaker, NodePath, TransparencyAttrib, Vec4
        """
        Load image as 3d plane
        
        Arguments:
        filepath -- image file path
        yresolution -- pixel-perfect width resolution
        """
        
        tex = loader.loadTexture(filepath)
        tex.setBorderColor(Vec4(0,0,0,0))
        tex.setWrapU(Texture.WMBorderColor)
        tex.setWrapV(Texture.WMBorderColor)
        cm = CardMaker(filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
        card = NodePath(cm.generate())
        card.setTexture(tex)
        card.setScale(card.getScale()/ yresolution)
        card.flattenLight() # apply scale
        card.setTransparency(TransparencyAttrib.MBinary)
        return card
    
    def updateSnowballButton(self):
        from panda3d.core import TextNode, Vec4
        if not self.__snowballButton:
            gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
            upButton = gui.find('**/InventoryButtonUp')
            dnButton = gui.find('**/InventoryButtonDown')
            rlvrButton = gui.find('**/InventoryButtonRollover')
            self.__snowballButton = DirectButton(image = (upButton, dnButton, rlvrButton), 
                geom = self.loadImageAsPlane('winter/maps/snowball_icon.png'), 
                text='50', 
                text_scale=0.04, 
                text_align=TextNode.ARight, 
                geom_scale=0.85, 
                geom_pos=(0, 0, 0), 
                text_fg=Vec4(1, 1, 1, 1), 
                text_pos=(0.07, -0.04), 
                relief=None,
                image_color=(0, 0.6, 1, 1), 
            pos=(0, 0.1, 0.7))
        

    def prepareToSwitchControlType(self):
        # Hack fix for getting stuck moving in one direction without pressing the movement keys.
        inputs = [
            "run",
            "forward",
            "reverse",
            "turnLeft",
            "turnRight",
            "slideLeft",
            "slideRight",
            "jump"
        ]
        for inputName in inputs:
            try:
                inputState.releaseInputs(inputName)
            except:
                pass

    def getBackpack(self):
        return DistributedToon.getBackpack(self)

    def setMyBattle(self, battle):
        self.myBattle = battle

    def getMyBattle(self):
        return self.myBattle

    def ghostOn(self):
        self.getGeomNode().setTransparency(1)
        self.getGeomNode().setColorScale(1, 1, 1, 0.25)

    def ghostOff(self):
        self.getGeomNode().setColorScale(1, 1, 1, 1)
        self.getGeomNode().setTransparency(0)

    def enterReadBook(self, ts = 0, callback = None, extraArgs = []):
        self.stopLookAround()
        self.b_lookAtObject(0, -45, 0)
        DistributedToon.enterReadBook(self, ts, callback, extraArgs)

    def exitReadBook(self):
        DistributedToon.exitReadBook(self)
        self.startLookAround()

    def getAirborneHeight(self):
        return self.offset + 0.025000000000000001

    def setupControls(self):
        self.walkControls = GravityWalker(legacyLifter=False)
        self.walkControls.setWallBitMask(CIGlobals.WallBitmask)
        self.walkControls.setFloorBitMask(CIGlobals.FloorBitmask)
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
            CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
        )
        self.walkControls.initializeCollisions(base.cTrav, self, floorOffset=0.025, reach=4.0)
        self.walkControls.setAirborneHeightFunc(self.getAirborneHeight)

    def setWalkSpeedNormal(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
            CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
        )

    def setWalkSpeedSlow(self):
        self.walkControls.setWalkSpeed(
            CIGlobals.ToonForwardSlowSpeed, CIGlobals.ToonJumpSlowForce,
            CIGlobals.ToonReverseSlowSpeed, CIGlobals.ToonRotateSlowSpeed
        )

    def setupCamera(self):
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
        camHeight = max(self.getHeight(), 3.0)
        heightScaleFactor = camHeight * 0.3333333333
        defLookAt = Point3(0.0, 1.5, camHeight)
        camPos = (Point3(0.0, -9.0 * heightScaleFactor, camHeight),
            defLookAt,
            Point3(0.0, camHeight, camHeight * 4.0),
            Point3(0.0, camHeight, camHeight * -1.0),
            0)
        self.smartCamera.initializeSmartCamera()
        self.smartCamera.setIdealCameraPos(camPos[0])
        self.smartCamera.setLookAtPoint(defLookAt)

    def setDNAStrand(self, dnaStrand):
        DistributedToon.setDNAStrand(self, dnaStrand)
        self.initCollisions()
        self.setupCamera()

    def setMoney(self, money):
        DistributedToon.setMoney(self, money)
        self.moneyGui.update(money)

    def setupNameTag(self, tempName = None):
        DistributedToon.setupNameTag(self, tempName)
        if self.nameTag:
            self.nameTag.setColorLocal()

    def d_broadcastPositionNow(self):
        self.d_clearSmoothing()
        self.d_broadcastPosHpr()

    def b_setAnimState(self, anim, callback = None, extraArgs = []):
        if self.anim != anim:
            self.d_setAnimState(anim)
            DistributedToon.setAnimState(self, anim, callback = callback, extraArgs = extraArgs)

    def attachCamera(self):
        #self.notify.info("Attaching camera...")
        camera.reparentTo(self)
        camera.setPos(self.smartCamera.getIdealCameraPos())

    def startSmartCamera(self):
        #self.notify.info("Starting camera...")
        self.smartCamera.startUpdateSmartCamera()

    def resetSmartCamera(self):
        #self.notify.info("Resetting camera...")
        self.stopSmartCamera()
        self.startSmartCamera()

    def stopSmartCamera(self):
        #self.notify.info("Stopping camera...")
        self.smartCamera.stopUpdateSmartCamera()

    def detachCamera(self):
        #self.notify.info("Detaching camera...")
        camera.reparentTo(render)
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)

    def handleSuitAttack(self, attack_id, suit_id):
        DistributedToon.handleSuitAttack(self, attack_id, suit_id)
        if not self.isDead() and base.config.GetBool('want-sa-reactions'):
            base.taskMgr.remove('LT.attackReactionDone')
            attack = SuitAttacks.SuitAttackLengths.keys()[attack_id]
            suit = self.cr.doId2do.get(suit_id)
            animToPlay = None
            timeToWait = 3.0
            if not attack in ["pickpocket", "fountainpen"]:
                suitH = suit.getH(render) % 360
                myH = self.getH(render) % 360
                if -90.0 <= (suitH - myH) <= 90.0:
                    animToPlay = "fallFWD"
                else:
                    animToPlay = "fallBCK"
            elif attack in ["pickpocket"]:
                animToPlay = "cringe"
            elif attack in ["fountainpen"]:
                animToPlay = "conked"
                timeToWait = 5.0
            self.cr.playGame.getPlace().fsm.request('stop')
            self.b_setAnimState(animToPlay)
            base.taskMgr.doMethodLater(timeToWait, self.__attackReactionDone, 'LT.attackReactionDone')

    def __attackReactionDone(self, task):
        self.cr.playGame.hood.loader.place.fsm.request('walk')
        self.b_setAnimState('neutral')
        return Task.done

    def enableAvatarControls(self):
        self.walkControls.enableAvatarControls()
        self.accept("control", self.updateMovementKeymap, ["jump", 1])
        self.accept("control-up", self.updateMovementKeymap, ["jump", 0])
        taskMgr.add(self.movementTask, "avatarMovementTask")
        self.avatarMovementEnabled = True
        self.playMovementSfx(None)

    def disableAvatarControls(self):
        self.walkControls.disableAvatarControls()
        self.ignore("arrow_up")
        self.ignore("arrow_up-up")
        self.ignore("arrow_down")
        self.ignore("arrow_down-up")
        self.ignore("arrow_left")
        self.ignore("arrow_left-up")
        self.ignore("arrow_right")
        self.ignore("arrow_right-up")
        self.ignore("control")
        self.ignore("control-up")
        taskMgr.remove("avatarMovementTask")
        self.isMoving_forward = False
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_jump = False
        self.avatarMovementEnabled = False
        self.playMovementSfx(None)
        for k, _ in self.movementKeymap.items():
            self.updateMovementKeymap(k, 0)

    def updateMovementKeymap(self, key, value):
        self.movementKeymap[key] = value

    def getMovementKeyValue(self, key):
        return self.movementKeymap[key]

    def playMovementSfx(self, movement):
        if movement == "run":
            self.walkSfx.stop()
            self.runSfx.play()
        elif movement == "walk":
            self.runSfx.stop()
            self.walkSfx.play()
        else:
            self.runSfx.stop()
            self.walkSfx.stop()

    def __forward(self):
        self.resetHeadHpr()
        self.stopLookAround()
        if self.getHealth() < 1:
            self.playMovementSfx("walk")
            self.setPlayRate(1.2, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.playMovementSfx("run")
            self.setAnimState('run')
        self.isMoving_side = False
        self.isMoving_back = False
        self.isMoving_forward = True
        self.isMoving_jump = False

    def __turn(self):
        self.resetHeadHpr()
        self.stopLookAround()
        self.playMovementSfx("walk")
        if self.getHealth() < 1:
            self.setPlayRate(1.2, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.setPlayRate(1.0, "walk")
            self.setAnimState("walk")
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_side = True
        self.isMoving_jump = False

    def __reverse(self):
        self.resetHeadHpr()
        self.stopLookAround()
        self.playMovementSfx("walk")
        if self.getHealth() < 1:
            self.setPlayRate(-1.0, 'dwalk')
            self.setAnimState('deadWalk')
        else:
            self.setAnimState("walkBack")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = True
        self.isMoving_jump = False

    def __jump(self):
        self.playMovementSfx(None)
        if base.localAvatar.getHealth() > 0:
            if self.playingAnim == 'run' or self.playingAnim == 'walk':
                self.b_setAnimState("leap")
            else:
                self.b_setAnimState("jump")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_jump = True

    def __neutral(self):
        self.resetHeadHpr()
        self.startLookAround()
        self.playMovementSfx(None)
        if base.localAvatar.getHealth() > 0:
            self.setAnimState("neutral")
        else:
            self.setPlayRate(1.0, 'dneutral')
            self.setAnimState("deadNeutral")
        self.isMoving_side = False
        self.isMoving_forward = False
        self.isMoving_back = False
        self.isMoving_jump = False

    def movementTask(self, task):
        if self.getMovementKeyValue("jump") == 1:
            if not self.walkControls.isAirborne:
                if self.walkControls.mayJump:
                    self.__jump()
                    self.hasDoneJump = True
                else:
                    if self.hasDoneJump:
                        if self.getHealth() > 0:
                            self.b_setAnimState('Happy')
                        self.hasDoneJump = False
        else:
            if not self.walkControls.isAirborne:
                if self.hasDoneJump:
                    if self.getHealth() > 0:
                        self.b_setAnimState('Happy')
                    self.hasDoneJump = False
        return task.cont

    def startTrackAnimToSpeed(self):
        base.taskMgr.add(self.trackAnimToSpeed, self.uniqueName('trackAnimToSpeed'))

    def stopTrackAnimToSpeed(self):
        base.taskMgr.remove(self.uniqueName('trackAnimToSpeed'))

    def trackAnimToSpeed(self, task):
        speed, rotSpeed, slideSpeed = self.walkControls.getSpeeds()
        state = None
        if self.getHealth() > 0:
            state = 'Happy'
        else:
            state = 'Sad'
        if state != self.lastState:
            self.lastState = state
            self.b_setAnimState(state)
            if state == 'Sad':
                self.setWalkSpeedSlow()
            else:
                self.setWalkSpeedNormal()
        action = self.setSpeed(speed, rotSpeed)
        if action != self.lastAction:
            self.lastAction = action
            if action == CIGlobals.WALK_INDEX or action == CIGlobals.REVERSE_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
                self.playMovementSfx("walk")
            elif action == CIGlobals.RUN_INDEX:
                self.resetHeadHpr()
                self.stopLookAround()
                self.playMovementSfx("run")
            else:
                self.resetHeadHpr()
                self.startLookAround()
                self.playMovementSfx(None)
        return task.cont

    def createLaffMeter(self):
        r, g, b, _ = self.getHeadColor()
        animal = self.getAnimal()
        maxHp = self.getMaxHealth()
        hp = self.getHealth()
        self.laffMeter.generate(r, g, b, animal, maxHP = maxHp, initialHP = hp)
        self.laffMeter.start()

    def disableLaffMeter(self):
        self.laffMeter.stop()
        self.laffMeter.disable()

    def deleteLaffMeter(self):
        self.laffMeter.delete()

    def setLoadout(self, gagIds):
        DistributedToon.setLoadout(self, gagIds)
        if base.cr.playGame.getPlace() and base.cr.playGame.getPlace().fsm.getCurrentState().getName() == 'shtickerBook':
            if hasattr(base.cr.playGame.getPlace(), 'shtickerBookStateData'):
                if base.cr.playGame.getPlace().shtickerBookStateData.fsm.getCurrentState().getName() == 'inventoryPage':
                    base.cr.playGame.getPlace().shtickerBookStateData.gui.fsm.request('idle')

    def enablePies(self, andKeys = 0):
        if self.avatarMovementEnabled and andKeys:
            self.enablePieKeys()
        self.backpack = DistributedToon.getBackpack(self)
        self.invGui = InventoryGui()
        self.invGui.createGui()
        self.invGui.setBackpack(self.backpack)
        for gag in self.backpack.getGags():
            gag.setAvatar(self)
        self.backpack.setGagGUI(self.invGui)
        if self.backpack.getCurrentGag():
            self.invGui.setWeapon(self.backpack.getCurrentGag().getName(), playSound = False)

    def enablePieKeys(self):
        if self.pieThrowBtn:
            if not self.backpack:
                self.backpack = DistributedToon.getBackpack(self)
            self.pieThrowBtn.bind(DGG.B1PRESS, self.startGag)
            self.pieThrowBtn.bind(DGG.B1RELEASE, self.throwGag)
        self.accept("delete", self.startGag)
        self.accept("delete-up", self.throwGag)

    def disablePieKeys(self):
        if self.pieThrowBtn:
            self.pieThrowBtn.unbind(DGG.B1PRESS)
            self.pieThrowBtn.unbind(DGG.B1RELEASE)
        self.ignore("delete")
        self.ignore("delete-up")

    def disablePies(self):
        self.disablePieKeys()
        self.invGui.deleteGui()
        if hasattr(self, 'backpack'):
            if self.backpack:
                self.backpack.setCurrentGag(None)

    def setWeaponType(self, weaponType):
        enableKeysAgain = 0
        if weaponType != self.weaponType:
            enableKeysAgain = 1
        self.weaponType = weaponType
        if enableKeysAgain:
            self.disablePieKeys()
            self.enablePieKeys()

    def createMoney(self):
        self.moneyGui.createGui()
        # Automatically update incase we missed the db field.
        self.moneyGui.update(self.money)

    def handleMoneyChanged(self):
        self.moneyGui.update()

    def disableMoney(self):
        self.moneyGui.deleteGui()

    def resetHeadHpr(self):
        self.b_lookAtObject(0, 0, 0, blink = 0)

    def startGag(self, start = True):
        if not self.backpack or not self.backpack.getCurrentGag():
            return
        if self.backpack.getSupply() > 0:
            if self.pieThrowBtn:
                self.pieThrowBtn.unbind(DGG.B1PRESS)
            if self.backpack.getActiveGag():
                if self.backpack.getActiveGag().getState() != GagState.LOADED:
                    return
            self.ignore("delete")
            self.backpack.getCurrentGag().setAvatar(self)
            self.resetHeadHpr()
            self.b_gagStart(self.backpack.getCurrentGag().getID())

    def throwGag(self, start = True):
        if not self.backpack or not self.backpack.getCurrentGag() or not self.backpack.getActiveGag():
            return
        if self.backpack.getSupply() > 0:
            if self.pieThrowBtn:
                self.pieThrowBtn.unbind(DGG.B1RELEASE)
            self.ignore("delete-up")
            if self.backpack.getActiveGag().getType() == GagType.SQUIRT and self.backpack.getActiveGag().getName() in [CIGlobals.SeltzerBottle]:
                self.b_gagRelease(self.backpack.getActiveGag().getID())
            else:
                self.b_gagThrow(self.backpack.getActiveGag().getID())
            activeGag = self.backpack.getActiveGag()
            if not activeGag:
                activeGag = self.backpack.getCurrentGag()
            if not activeGag.doesAutoRelease():
                Sequence(Wait(0.75), Func(self.releaseGag), Wait(0.3), Func(self.enablePieKeys)).start()

    def releaseGag(self):
        if not self.backpack or not self.backpack.getActiveGag():
            return
        if self.backpack.getSupply() > 0:
            gag = self.backpack.getActiveGag()
            if not gag:
                gag = self.backpack.getCurrentGag()
            if gag.getState() != GagState.RELEASED:
                gagName = gag.getName()
                self.b_gagRelease(GagGlobals.getIDByName(gagName))

    def checkSuitHealth(self, suit):
        pass

    def handleLookSpot(self, hpr):
        h, p, r = hpr
        self.d_lookAtObject(h, p, r, blink = 1)

    def showPieButton(self):
        geom = CIGlobals.getDefaultBtnGeom()
        self.pieThrowBtn = DirectButton(
            geom = geom,
            geom_scale = (0.75, 1, 1),
            text = "Throw Gag",
            text_scale = 0.05,
            text_pos = (0, -0.01),
            relief = None,
            parent = base.a2dTopCenter,
            pos = (0, 0, -0.1)
        )
        self.pieThrowBtn.setBin('gui-popup', 60)

    def hidePieButton(self):
        self.pieThrowBtn.removeNode()
        self.pieThrowBtn = None

    def showBookButton(self, inBook = 0):
        self.book_gui = loader.loadModel("phase_3.5/models/gui/sticker_open_close_gui.bam")
        self.book_btn = DirectButton(
            geom=(
                self.book_gui.find('**/BookIcon_CLSD'),
                self.book_gui.find('**/BookIcon_OPEN'),
                self.book_gui.find('**/BookIcon_RLVR')
            ),
            relief=None,
            pos=(-0.175, 0, 0.163),
            command=self.bookButtonClicked,
            scale=(0.7, 0.8, 0.8),
            parent=base.a2dBottomRight
        )
        self.book_btn.setBin('gui-popup', 60)
        if inBook:
            self.book_btn["geom"] = (
                self.book_gui.find('**/BookIcon_OPEN'),
                self.book_gui.find('**/BookIcon_CLSD'),
                self.book_gui.find('**/BookIcon_RLVR2')
            )
            self.book_btn["command"] = self.bookButtonClicked
            self.book_btn["extraArgs"] = [0]

    def hideBookButton(self):
        if hasattr(self, 'book_gui'):
            self.book_gui.removeNode()
            del self.book_gui
        if hasattr(self, 'book_btn'):
            self.book_btn.destroy()
            del self.book_btn

    def bookButtonClicked(self, openIt = 1):
        if openIt:
            base.cr.playGame.getPlace().fsm.request('shtickerBook')
        else:
            base.cr.playGame.getPlace().shtickerBookStateData.finished("resume")

    def startMonitoringHP(self):
        taskMgr.add(self.monitorHealth, "localToon-monitorHealth")

    def monitorHealth(self, task):
        if self.isDead():
            base.taskMgr.remove("LT.attackReactionDone")
            if self.cr.playGame.hood.id != ZoneUtil.getHoodId(self.zoneId):
                self.cr.playGame.getPlace().fsm.request('died', [{}, self.diedStateDone])
            return task.done
        return task.cont

    def stopMonitoringHP(self):
        taskMgr.remove("localToon-monitorHealth")

    def setHealth(self, hp):
        if hp > 0 and self.getHealth() < 1:
            if self.cr.playGame.getPlace():
                if self.cr.playGame.getPlace().fsm.getCurrentState().getName() == 'walk':
                    if self.cr.playGame.getPlace().walkStateData.fsm.getCurrentState().getName() == 'deadWalking':
                        self.cr.playGame.getPlace().walkStateData.fsm.request('walking')
            if self.animFSM.getCurrentState().getName() == 'deadNeutral':
                self.playMovementSfx(None)
                self.b_setAnimState("neutral")
            elif self.animFSM.getCurrentState().getName() == 'deadWalk':
                self.playMovementSfx("run")
                self.b_setAnimState("run")
        DistributedToon.setHealth(self, hp)


    def diedStateDone(self, requestStatus):
        hood = self.cr.playGame.hood.id
        if hood == CIGlobals.BattleTTC:
            hood = CIGlobals.ToontownCentral
        toZone = ZoneUtil.getZoneId(hood)
        if self.zoneId != toZone:
            requestStatus = {'zoneId': toZone,
                        'hoodId': hood,
                        'where': ZoneUtil.getWhereName(toZone),
                        'avId': self.doId,
                        'loader': ZoneUtil.getLoaderName(toZone),
                        'shardId': None,
                        'wantLaffMeter': 1,
                        'how': 'teleportIn'}
            self.cr.playGame.getPlace().doneStatus = requestStatus
            messenger.send(self.cr.playGame.getPlace().doneEvent)

        else: return

        ## Tell the ai we're dead so they can refill our hp.
        #self.sendUpdate("died", [])
        ## Then, log out and notify the client that they're dead.
        # self.cr.gameFSM.request("closeShard", ['died'])

    def teleportToCT(self):
        toZone = CIGlobals.CogTropolisId
        hood = CIGlobals.CogTropolis
        requestStatus = {'zoneId': toZone,
                'hoodId': hood,
                'where': ZoneUtil.getWhereName(toZone),
                'avId': self.doId,
                'loader': ZoneUtil.getLoaderName(toZone),
                'shardId': None,
                'wantLaffMeter': 1,
                'how': 'teleportIn'}
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])

    def createChatInput(self):
        self.chatInput.load()
        self.chatInput.enter()

    def disableChatInput(self):
        self.chatInput.exit()
        self.chatInput.unload()

    def collisionsOn(self):
        self.controlManager.collisionsOn()

    def collisionsOff(self):
        self.controlManager.collisionsOff()

    def generate(self):
        DistributedToon.generate(self)

    def delete(self):
        DistributedToon.delete(self)
        self.deleteLaffMeter()
        return

    def disable(self):
        base.camLens.setMinFov(CIGlobals.OriginalCameraFov / (4./3.))
        self.friendsList.destroy()
        self.friendsList = None
        self.positionExaminer.delete()
        self.positionExaminer = None
        self.disablePicking()
        self.stopMonitoringHP()
        taskMgr.remove("resetHeadColorAfterFountainPen")
        taskMgr.remove("LT.attackReactionDone")
        self.stopLookAround()
        DistributedToon.disable(self)
        self.disableAvatarControls()
        self.disableLaffMeter()
        self.disablePies()
        self.disableChatInput()
        self.weaponType = None
        self.pieType = None
        self.myBattle = None
        self.ignore("gotLookSpot")
        return

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        self.setupPicker()
        self.setupControls()
        #self.createChatInput()
        self.startLookAround()
        self.friendRequestManager.watch()
        self.accept('enter', self.printAvPos)
        self.accept('p', self.enterPictureMode)
        #self.accept('c', self.teleportToCT)
        #posBtn = DirectButton(text = "Get Pos", scale = 0.08, pos = (0.3, 0, 0), parent = base.a2dLeftCenter, command = self.printAvPos)
        self.accept("gotLookSpot", self.handleLookSpot)
        
    def enterPictureMode(self):
        self.laffMeter.stop()
        self.laffMeter.disable()
        self.laffMeter.destroy()
        self.getGeomNode().hide()
        self.deleteNameTag()
        self.moneyGui.deleteGui()
        self.invGui.deleteGui()
        self.hidePieButton()
        self.hideFriendButton()
        self.hideBookButton()
        self.removeAdminToken()

    def printAvPos(self):
        print "Pos: %s, Hpr: %s" % (self.getPos(), self.getHpr())
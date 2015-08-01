# Filename: CameraShyFirstPerson.py
# Created by:  blach (28Apr15)

from panda3d.core import BitMask32, CollisionNode, CollisionRay, CollisionHandlerEvent, VBase4
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.gui.DirectGui import OnscreenText, DirectFrame, DirectWaitBar, OnscreenImage
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import Sequence, Func, Wait

from FirstPerson import FirstPerson
from lib.coginvasion.globals import CIGlobals

class CameraShyFirstPerson(FirstPerson):
	toonInFocusColor = VBase4(0.25, 1.0, 0.25, 1.0)
	toonOutOfFocusColor = VBase4(1.0, 1.0, 1.0, 1.0)
	fullyChargedState = 5

	def __init__(self, mg):
		self.mg = mg
		self.cameraFocus = None
		self.batteryFrame = None
		self.batteryBg = None
		self.batteryBar = None
		self.rechargeSound = None
		self.fullyChargedSound = None

		self.hasToonInFocus = False
		self.toonToTakePicOf = None

		self.cameraRechargeState = None
		self.cameraRechargingLabel = None
		self.cameraFlashSeq = None

		self.camFSM = ClassicFSM(
			'CameraFSM',
			[
				State('off', self.enterOff, self.exitOff),
				State('ready', self.enterCameraReady, self.exitCameraReady),
				State('recharge', self.enterCameraRecharge, self.exitCameraRecharge)
			],
			'off', 'off'
		)
		self.camFSM.enterInitialState()
		FirstPerson.__init__(self)

	def movementTask(self, task):
		if (
			not inputState.isSet('jump') and
			not base.localAvatar.walkControls.isAirborne and
			inputState.isSet('forward') or
			inputState.isSet('reverse') or
			inputState.isSet('slideLeft') or
			inputState.isSet('slideRight')
		):
			if base.localAvatar.getAnimState() != "run":
				base.localAvatar.setAnimState('run')
				base.localAvatar.playMovementSfx("run")
				self.mg.sendUpdate("runningAvatar", [base.localAvatar.doId])
		elif (
			inputState.isSet('jump') or
			base.localAvatar.walkControls.isAirborne
		):
			if base.localAvatar.getAnimState() != "jump":
				base.localAvatar.setAnimState("jump")
				base.localAvatar.playMovementSfx(None)
				self.mg.sendUpdate("jumpingAvatar", [base.localAvatar.doId])
		else:
			if base.localAvatar.getAnimState() != "neutral":
				base.localAvatar.setAnimState("neutral")
				base.localAvatar.playMovementSfx(None)
				self.mg.sendUpdate("standingAvatar", [base.localAvatar.doId])
		return task.cont

	def enterOff(self):
		pass

	def exitOff(self):
		pass

	def enterCameraReady(self):
		self.acceptOnce("mouse1", self.__mouse1Pressed)

	def stopCameraFlash(self):
		if self.cameraFlashSeq:
			self.cameraFlashSeq.finish()
			self.cameraFlashSeq = None

	def __mouse1Pressed(self):
		self.cameraFlashSeq = Sequence(
			Func(base.transitions.setFadeColor, 1, 1, 1),
			Func(base.transitions.fadeOut, 0.1),
			Wait(0.1),
			Func(base.transitions.fadeIn, 0.1),
			Wait(0.1),
			Func(base.transitions.setFadeColor, 0, 0, 0)
		)
		self.cameraFlashSeq.start()
		self.mg.sendUpdate('remoteAvatarTakePicture', [base.localAvatar.doId])
		self.mg.myRemoteAvatar.takePicture()
		if self.hasToonInFocus and self.toonToTakePicOf:
			self.mg.sendUpdate('tookPictureOfToon', [self.toonToTakePicOf.doId])
		self.camFSM.request('recharge')

	def exitCameraReady(self):
		self.ignore("mouse1")

	def enterCameraRecharge(self):
		self.batteryBar.update(0)
		taskMgr.add(self.__rechargeNextState, "rechargeCamera")

	def __rechargeNextState(self, task):
		if self.cameraRechargeState == None:
			self.cameraRechargeState = -1
		self.cameraRechargeState += 1
		if self.cameraRechargeState > 0:
			base.playSfx(self.rechargeSound)
		self.batteryBar.update(self.cameraRechargeState)
		if self.cameraRechargeState == self.fullyChargedState:
			base.playSfx(self.fullyChargedSound)
			self.camFSM.request('ready')
			return task.done
		task.delayTime = 1.0
		return task.again

	def exitCameraRecharge(self):
		taskMgr.remove("rechargeCamera")
		self.cameraRechargeState = None

	def __handleRayInto(self, entry):
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in base.cr.doId2do.keys():
			obj = base.cr.doId2do[key]
			if obj.__class__.__name__ == "DistributedToon":
				if obj.getKey() == toonNP.getKey():
					self.__handleToonInFocus(obj)

	def __handleRayOut(self, entry):
		intoNP = entry.getIntoNodePath()
		toonNP = intoNP.getParent()
		for key in base.cr.doId2do.keys():
			obj = base.cr.doId2do[key]
			if obj.__class__.__name__ == "DistributedToon":
				if obj.getKey() == toonNP.getKey():
					self.toonToTakePicOf = None
					self.hasToonInFocus = False
					if self.cameraFocus.getColorScale() == self.toonInFocusColor:
						self.cameraFocus.setColorScale(self.toonOutOfFocusColor)

	def __handleToonInFocus(self, toon):
		if not self.hasToonInFocus or self.toonToTakePicOf is not None or self.toonToTakePicOf.doId != toon.doId:
			self.toonToTakePicOf = toon
			self.hasToonInFocus = True
			self.cameraFocus.setColorScale(self.toonInFocusColor)

	def start(self):
		self.fullyChargedSound = base.loadSfx('phase_4/audio/sfx/MG_pairing_match.mp3')
		self.rechargeSound = base.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_blue_arrow.mp3')
		self.batteryFrame = DirectFrame(parent = base.a2dBottomRight, pos = (-0.2, 0, 0.1), scale = (0.8, 0, 1))
		self.batteryBg = OnscreenImage(image = 'phase_4/maps/battery_charge_frame.png', parent = self.batteryFrame)
		self.batteryBg.setTransparency(1)
		self.batteryBg.setX(0.03)
		self.batteryBg.setScale(0.17, 0, 0.05)
		self.batteryBar = DirectWaitBar(value = 0, range = 5, barColor = (1, 1, 1, 1), relief = None, scale = (0.12, 0.0, 0.3), parent = self.batteryFrame)
		self.cameraFocus = loader.loadModel("phase_4/models/minigames/photo_game_viewfinder.bam")
		self.cameraFocus.reparentTo(base.aspect2d)
		self.focusCollHandler = CollisionHandlerEvent()
		self.focusCollHandler.setInPattern("%fn-into")
		self.focusCollHandler.setOutPattern("%fn-out")
		self.focusCollNode = CollisionNode('mouseRay')
		self.focusCollNP = base.camera.attachNewNode(self.focusCollNode)
		self.focusCollNode.setCollideMask(BitMask32(0))
		self.focusCollNode.setFromCollideMask(CIGlobals.WallBitmask)
		self.focusRay = CollisionRay()
		self.focusRay.setFromLens(base.camNode, 0.0, 0.0)
		self.focusCollNode.addSolid(self.focusRay)
		base.cTrav.addCollider(self.focusCollNP, self.focusCollHandler)
		base.localAvatar.walkControls.setWalkSpeed(
			CIGlobals.ToonForwardSpeed, 0.0,
			CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
		)
		FirstPerson.start(self)

	def reallyStart(self):
		self.accept("mouseRay-into", self.__handleRayInto)
		self.accept("mouseRay-out", self.__handleRayOut)
		self.camFSM.request('recharge')
		taskMgr.add(self.movementTask, "movementTask")
		FirstPerson.reallyStart(self)

	def end(self):
		self.camFSM.request('off')
		taskMgr.remove("movementTask")
		self.ignore("mouseRay-into")
		self.ignore("mouseRay-out")
		FirstPerson.end(self)

	def reallyEnd(self):
		self.batteryBar.destroy()
		self.batteryBar = None
		self.batteryBg.destroy()
		self.batteryBg = None
		self.batteryFrame.destroy()
		self.batteryFrame = None
		self.cameraFocus.removeNode()
		self.cameraFocus = None
		self.focusCollHandler = None
		self.focusCollNode = None
		self.focusCollNP.removeNode()
		self.focusCollNP = None
		self.focusRay = None
		self.hasToonInFocus = None
		self.toonToTakePicOf = None
		self.fullyChargedSound = None
		self.rechargeSound = None
		self.stopCameraFlash()
		FirstPerson.reallyEnd(self)
		base.localAvatar.walkControls.setWalkSpeed(
			CIGlobals.ToonForwardSpeed, CIGlobals.ToonJumpForce,
			CIGlobals.ToonReverseSpeed, CIGlobals.ToonRotateSpeed
		)

	def cleanup(self):
		self.camFSM.requestFinalState()
		self.camFSM = None
		FirstPerson.cleanup(self)

"""

  Filename: ToonTalker.py
  Created by: blach (??July14)

"""

from lib.coginvasion.globals import CIGlobals
from pandac.PandaModules import *
from panda3d.core import *
from direct.gui.DirectGui import *
from lib.coginvasion.toon.LabelScaler import LabelScaler
from direct.directnotify.DirectNotify import DirectNotify
from lib.coginvasion.toon.ChatBalloon import ChatBalloon
import random
import math

notify = DirectNotify().newCategory("ToonTalker")

class ToonTalker:
	THOUGHT_PREFIX = '.'
	LENGTH_FACTOR = 0.6
	MIN_LENGTH = 5
	MAX_LENGTH = 20

	def __init__(self):
		self.avatar = None
		self.nametag = None

	def setAvatar(self, avatar, nametag):
		self.avatar = avatar
		self.nametag = nametag

	def setChatAbsolute(self, chatString = None):
		if not chatString or chatString.isspace() or len(chatString) == 0:
			return

		self.clearChat()
		self.taskId = random.randint(0, 1000000000000000000000000000000)
		self.nameTag.hide()

		if self.isThought(chatString):
			chatString = self.removeThoughtPrefix(chatString)
			bubble = loader.loadModel(CIGlobals.ThoughtBubble)
		else:
			length = math.sqrt(len(chatString)) / self.LENGTH_FACTOR
			if length < self.MIN_LENGTH:
				length = self.MIN_LENGTH
			if length > self.MAX_LENGTH:
				length = self.MAX_LENGTH
			bubble = loader.loadModel(CIGlobals.ChatBubble)
			taskMgr.doMethodLater(length, self.clearChatTask, "clearAvatarChat-%s" % (str(self.taskId)))

		if self.avatarType == CIGlobals.Suit:
			font = CIGlobals.getSuitFont()
		else:
			font = CIGlobals.getToonFont()

		self.chatBubble = ChatBalloon(bubble).generate(chatString, font)
		self.chatBubble.setEffect(BillboardEffect.make(Vec3(0,0,1), True, False, 3.0, camera, Point3(0,0,0)))
		self.chatBubble.setZ(self.nameTag.getZ())

		if hasattr(self.avatar, 'getGhost'):
			if not self.avatar.getGhost() or self.avatar.doId == base.localAvatar.doId:
				self.chatBubble.reparentTo(self)
		else:
			self.chatBubble.reparentTo(self)

		LabelScaler().resize(self.chatBubble)

	def isThought(self, message):
		if message.isspace():
			return False
		if message[0] == self.THOUGHT_PREFIX:
			return True
		else:
			return False

	def removeThoughtPrefix(self, message):
		if self.isThought(message):
			return message[len(self.THOUGHT_PREFIX):]
		else:
			notify.warning("attempted to remove a thought prefix on a non-thought message")
			return message

	def clearChatTask(self, task):
		self.clearChat()
		return task.done

	def clearChat(self):
		try:
			self.chatBubble.removeNode()
			del self.chatBubble
		except:
			return
		if hasattr(self.avatar, 'getGhost'):
			if self.nameTag and not self.avatar.getGhost() or self.nameTag and self.avatar.doId == base.localAvatar.doId:
				self.nameTag.show()
		else:
			if self.nameTag:
				self.nameTag.show()
		taskMgr.remove("clearAvatarChat-" + str(self.taskId))

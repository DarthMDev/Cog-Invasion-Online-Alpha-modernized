"""

  Filename: GunGameLevelLoaderAI.py
  Created by: blach (23Apr15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import random

class GunGameLevelLoaderAI:
	notify = directNotify.newCategory("GunGameLevelLoaderAI")

	Levels = ['momada', 'dg', 'mml', 'cbhq']
	LevelData = {
		'momada': {
			'gameTime': 305
		},

		'dg': {
			'gameTime': 205
		},

		'mml': {
			'gameTime': 205
		},

		'cbhq': {
			'gameTime': 305
		}
	}

	def __init__(self, gun_game):
		self.game = gun_game
		self.level = ""

	def makeLevel(self):
		level = random.choice(self.Levels)
		self.setLevel(level)
		self.game.d_setLevelName(self.level)

	def setLevel(self, name):
		self.level = name

	def getLevel(self):
		return self.level

	def getGameTimeOfLevel(self, level):
		return self.LevelData[level]['gameTime']

	def getGameTimeOfCurrentLevel(self):
		return self.getGameTimeOfLevel(self.level)

	def cleanup(self):
		self.level = None
		self.game = None

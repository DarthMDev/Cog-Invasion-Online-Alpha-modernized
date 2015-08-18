"""

  Filename: Suit.py
  Created by: blach (??July14)

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.avatar import Avatar
from direct.directnotify.DirectNotify import DirectNotify
from direct.gui.DirectGui import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.showbase import Audio3DManager
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.actor.Actor import Actor
from lib.coginvasion.toon import ParticleLoader
from direct.task.Task import Task
from direct.interval.IntervalGlobal import *
from direct.distributed import DelayDelete
from SuitAttacks import SuitAttacks
import random
import CogBattleGlobals
notify = DirectNotify().newCategory("Suit")

class Suit(Avatar.Avatar):
    healthColors = (Vec4(0, 1, 0, 1),
        Vec4(1, 1, 0, 1),
        Vec4(1, 0.5, 0, 1),
        Vec4(1, 0, 0, 1),
        Vec4(0.3, 0.3, 0.3, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
        Vec4(1, 1, 0.25, 0.5),
        Vec4(1, 0.5, 0.25, 0.5),
        Vec4(1, 0.25, 0.25, 0.5),
        Vec4(0.3, 0.3, 0.3, 0))
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
        's': Vec4(0.843, 0.745, 0.745, 1.0),
        'l': Vec4(0.749, 0.776, 0.824, 1.0),
        'm': Vec4(0.749, 0.769, 0.749, 1.0)}
    health2DmgMultiplier = 2.5

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.avatarType = CIGlobals.Suit
        self.name = ''
        self.chat = ''
        self.suit = None
        self.suitHeads = None
        self.suitHead = None
        self.loserSuit = None
        self.healthBarGlow = None
        self.healthBar = None
        self.weapon = None
        self.weapon_sfx = None
        self.anim = None
        self.suit_dial = None
        self.shadow = None
        self.balloon_sfx = None
        self.add_sfx = None
        self.explosion = None
        self.largeExp = None
        self.smallExp = None
        self.death_sfx = None
        self.attack = None
        self.wtrajectory = None
        self.throwObjectId = None
        self.hasSpawned = False
        self.suitTrack = None
        self.headModel = None
        self.condition = 0
        self.type = ""
        self.head = ""
        self.team = ""
        self.isSkele = 0
        self.timestampAnimTrack = None
        self.animFSM = ClassicFSM('Suit', [State('off', self.enterOff, self.exitOff),
                                State('neutral', self.enterNeutral, self.exitNeutral),
                                State('walk', self.enterWalk, self.exitWalk),
                                State('die', self.enterDie, self.exitDie),
                                State('attack', self.enterAttack, self.exitAttack),
                                State('flydown', self.enterFlyDown, self.exitFlyDown),
                                State('pie', self.enterPie, self.exitPie),
                                State('win', self.enterWin, self.exitWin),
                                State('flyaway', self.enterFlyAway, self.exitFlyAway),
                                State('rollodex', self.enterRollodex, self.exitRollodex),
                                State('flyNeutral', self.enterFlyNeutral, self.exitFlyNeutral),
                                State('flail', self.enterFlail, self.exitFlail),
                                State('drop', self.enterDrop, self.exitDrop),
                                State('drop-react', self.enterDropReact, self.exitDropReact),
                                State('squirt-large', self.enterLSquirt, self.exitLSquirt),
                                State('squirt-small', self.enterSSquirt, self.exitSSquirt)], 'off', 'off')
        animStateList = self.animFSM.getStates()
        self.animFSM.enterInitialState()

        self.initializeBodyCollisions()

    def delete(self):
        try:
            self.Suit_deleted
        except:
            self.Suit_deleted = 1
            Avatar.Avatar.delete(self)
            self.weapon = None
            self.weapon_sfx = None
            self.suit_dial = None
            del self.shadowPlacer

    def disable(self):
        if self.suitTrack:
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        self.animFSM.requestFinalState()
        self.cleanupSuit()
        self.animFSM = None
        self.avatarType = None
        self.name = None
        self.chat = None
        self.suit = None
        self.state = None
        self.weapon_state = None
        self.suitHeads = None
        self.suitHead = None
        self.loserSuit = None
        self.healthMeterGlow = None
        self.healthMeter = None
        self.weapon = None
        self.weapon_sfx = None
        self.anim = None
        self.suit_dial = None
        self.shadow = None
        self.balloon_sfx = None
        self.add_sfx = None
        self.explosion = None
        self.largeExp = None
        self.smallExp = None
        self.death_sfx = None
        self.attack = None
        self.wtrajectory = None
        self.throwObjectId = None
        self.hasSpawned = None
        self.suitTrack = None
        self.headModel = None
        self.condition = None
        self.type = None
        self.head = None
        self.team = None
        self.isSkele = None
        self.timestampAnimTrack = None
        Avatar.Avatar.disable(self)

    def generateSuit(self, suitType, suitHead, suitTeam, suitHealth, skeleton, hideFirst = True):
        self.type = suitType
        self.head = suitHead
        self.isSkele = skeleton
        self.team = suitTeam
        self.health = suitHealth
        self.maxHealth = suitHealth
        self.cleanupSuit()
        self.generateBody(suitType, suitTeam, suitHead, skeleton)
        self.generateHealthMeter()
        self.generateHead(suitType, suitHead)
        #self.setupNameTag()
        self.parentSuitParts()
        self.rescaleSuit()
        Avatar.Avatar.initShadow(self)
        if hideFirst:
            self.hide()

    def rescaleSuit(self):
        self.setAvatarScale(CIGlobals.SuitScales[self.head] / CIGlobals.SuitScaleFactors[self.type])

    def parentSuitParts(self):
        if not self.isSkele:
            self.headModel.reparentTo(self.find('**/joint_head'))

    def unparentSuitParts(self):
        self.getPart('body').reparentTo(self.getGeomNode())
        if not self.isSkele:
            self.headModel.reparentTo(self.getGeomNode())

    def generateBody(self, suitType, suitTeam, suitHead, skeleton):

        self.team = suitTeam
        self.type = suitType
        self.head = suitHead
        self.isSkele = skeleton

        if suitType == "A":
            if skeleton:
                self.loadModel("phase_5/models/char/cogA_robot-zero.bam", "body")
            else:
                self.loadModel("phase_3.5/models/char/suitA-mod.bam", "body")
            self.loadAnims({"neutral": "phase_4/models/char/suitA-neutral.bam",
                            "walk": "phase_4/models/char/suitA-walk.bam",
                            "pie": "phase_4/models/char/suitA-pie-small.bam",
                            "land": "phase_5/models/char/suitA-landing.bam",
                            "throw-object": "phase_5/models/char/suitA-throw-object.bam",
                            "throw-paper": "phase_5/models/char/suitA-throw-paper.bam",
                            "glower": "phase_5/models/char/suitA-glower.bam",
                            "win": "phase_4/models/char/suitA-victory.bam",
                            "rollodex": "phase_5/models/char/suitA-roll-o-dex.bam",
                            "pickpocket": "phase_5/models/char/suitA-pickpocket.bam",
                            "fountainpen": "phase_7/models/char/suitA-fountain-pen.bam",
                            "phone": "phase_5/models/char/suitA-phone.bam",
                            "flail": "phase_4/models/char/suitA-flailing.bam",
                            "drop" : "phase_5/models/char/suitA-drop.bam",
                            "drop-react" : "phase_5/models/char/suitA-anvil-drop.bam",
                            "squirt-large" : "phase_5/models/char/suitA-squirt-large.bam",
                            "squirt-small" : "phase_4/models/char/suitA-squirt-small.bam",
                            "slip-forward" : "phase_4/models/char/suitA-slip-forward.bam",
                            "slip-backward" : "phase_4/models/char/suitA-slip-backward.bam",
                            "sit": "phase_12/models/char/suitA-sit.bam"}, "body")
        if suitType == "B":
            if skeleton:
                self.loadModel("phase_5/models/char/cogB_robot-zero.bam", "body")
            else:
                self.loadModel("phase_3.5/models/char/suitB-mod.bam", "body")
            self.loadAnims({"neutral": "phase_4/models/char/suitB-neutral.bam",
                            "walk": "phase_4/models/char/suitB-walk.bam",
                            "pie": "phase_4/models/char/suitB-pie-small.bam",
                            "land": "phase_5/models/char/suitB-landing.bam",
                            "throw-object": "phase_5/models/char/suitB-throw-object.bam",
                            "throw-paper": "phase_5/models/char/suitB-throw-paper.bam",
                            "glower": "phase_5/models/char/suitB-magic1.bam",
                            "win": "phase_4/models/char/suitB-victory.bam",
                            "rollodex": "phase_5/models/char/suitB-roll-o-dex.bam",
                            "pickpocket": "phase_5/models/char/suitB-pickpocket.bam",
                            "fountainpen": "phase_5/models/char/suitB-pen-squirt.bam",
                            "phone": "phase_5/models/char/suitB-phone.bam",
                            "flail": "phase_4/models/char/suitB-flailing.bam",
                            "drop" : "phase_5/models/char/suitB-drop.bam",
                            "drop-react" : "phase_5/models/char/suitB-anvil-drop.bam",
                            "squirt-large" : "phase_5/models/char/suitB-squirt-large.bam",
                            "squirt-small" : "phase_4/models/char/suitB-squirt-small.bam",
                            "slip-forward" : "phase_4/models/char/suitB-slip-forward.bam",
                            "slip-backward" : "phase_4/models/char/suitB-slip-backward.bam",}, "body")
        if suitType == "C":
            if skeleton:
                self.loadModel("phase_5/models/char/cogC_robot-zero.bam", "body")
            else:
                self.loadModel("phase_3.5/models/char/suitC-mod.bam", "body")
            self.loadAnims({"neutral": "phase_3.5/models/char/suitC-neutral.bam",
                        "walk": "phase_3.5/models/char/suitC-walk.bam",
                        "pie": "phase_3.5/models/char/suitC-pie-small.bam",
                        "land": "phase_5/models/char/suitC-landing.bam",
                        "throw-object": "phase_3.5/models/char/suitC-throw-paper.bam",
                        "throw-paper": "phase_3.5/models/char/suitC-throw-paper.bam",
                        "glower": "phase_5/models/char/suitC-glower.bam",
                        "win": "phase_4/models/char/suitC-victory.bam",
                        "pickpocket": "phase_5/models/char/suitC-pickpocket.bam",
                        "fountainpen": "phase_5/models/char/suitC-fountain-pen.bam",
                        "phone": "phase_3.5/models/char/suitC-phone.bam",
                        "flail": "phase_4/models/char/suitC-flailing.bam",
                        "drop" : "phase_5/models/char/suitC-drop.bam",
                        "drop-react" : "phase_5/models/char/suitC-anvil-drop.bam",
                        "squirt-large" : "phase_5/models/char/suitC-squirt-large.bam",
                        "squirt-small" : "phase_3.5/models/char/suitC-squirt-small.bam",
                        "slip-forward" : "phase_4/models/char/suitC-slip-forward.bam",
                        "slip-backward" : "phase_4/models/char/suitC-slip-backward.bam",
                        "sit": "phase_12/models/char/suitC-sit.bam"}, "body")
        if skeleton:
            self.setTwoSided(1)

        if skeleton:
            if suitTeam == "s":
                self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_sales.jpg")
            elif suitTeam == "m":
                self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_money.jpg")
            elif suitTeam == "l":
                self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_legal.jpg")
            elif suitTeam == "c":
                self.suit_tie = loader.loadTexture("phase_5/maps/cog_robot_tie_boss.jpg")
            self.find('**/tie').setTexture(self.suit_tie, 1)
        else:
            if hasattr(self, 'getBattle') and self.getBattle() != None:
                if self.getBattle().getHoodIndex() == CogBattleGlobals.WaiterHoodIndex:
                    self.suit_blazer = loader.loadTexture("phase_3.5/maps/waiter_m_blazer.jpg")
                    self.suit_leg = loader.loadTexture("phase_3.5/maps/waiter_m_leg.jpg")
                    self.suit_sleeve = loader.loadTexture("phase_3.5/maps/waiter_m_sleeve.jpg")
            if not hasattr(self, 'getBattle') or self.getBattle() == None or self.getBattle().getHoodIndex() != CogBattleGlobals.WaiterHoodIndex:
                self.suit_blazer = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_blazer.jpg")
                self.suit_leg = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_leg.jpg")
                self.suit_sleeve = loader.loadTexture("phase_3.5/maps/" + suitTeam + "_sleeve.jpg")

            self.find('**/legs').setTexture(self.suit_leg, 1)
            self.find('**/arms').setTexture(self.suit_sleeve, 1)
            self.find('**/torso').setTexture(self.suit_blazer, 1)

            if suitHead == "coldcaller":
                self.find('**/hands').setColor(0.55, 0.65, 1.0, 1.0)
            elif suitHead == "corporateraider":
                self.find('**/hands').setColor(0.85, 0.55, 0.55, 1.0)
            elif suitHead == "bigcheese":
                self.find('**/hands').setColor(0.75, 0.95, 0.75, 1.0)
            elif suitHead == "bloodsucker":
                self.find('**/hands').setColor(0.95, 0.95, 1.0, 1.0)
            elif suitHead == "spindoctor":
                self.find('**/hands').setColor(0.5, 0.8, 0.75, 1.0)
            elif suitHead == "legaleagle":
                self.find('**/hands').setColor(0.25, 0.25, 0.5, 1.0)
            elif suitHead == "pennypincher":
                self.find('**/hands').setColor(1.0, 0.5, 0.6, 1.0)
            elif suitHead == "loanshark":
                self.find('**/hands').setColor(0.5, 0.85, 0.75, 1.0)
            else:
                self.find('**/hands').setColor(CIGlobals.SuitHandColors[suitTeam])

    def generateHead(self, suitType, suitHead):

        self.type = suitType
        self.head = suitHead

        if suitHead == "vp":
            self.headModel = Actor("phase_9/models/char/sellbotBoss-head-zero.bam")
            self.headModel.loadAnims({"neutral": "phase_9/models/char/bossCog-head-Ff_neutral.bam"})
            self.headModel.setTwoSided(True)
            self.headModel.loop("neutral")
            self.headModel.setScale(0.35)
            self.headModel.setHpr(270, 0, 270)
            self.headModel.setZ(-0.10)
        else:
            if suitType == "A" or suitType == "B":
                heads = loader.loadModel("phase_4/models/char/suit" + suitType + "-heads.bam")
            else:
                heads = loader.loadModel("phase_3.5/models/char/suit" + suitType + "-heads.bam")
            self.headModel = heads.find('**/' + CIGlobals.SuitHeads[suitHead])
            if suitHead == "flunky":
                glasses = heads.find('**/glasses')
                glasses.reparentTo(self.headModel)
                glasses.setTwoSided(True)
            if suitHead in CIGlobals.SuitSharedHeads:
                if suitHead == "coldcaller":
                    self.headModel.setColor(0.25, 0.35, 1.0, 1.0)
                else:
                    headTexture = loader.loadTexture("phase_3.5/maps/" + suitHead + ".jpg")
                    self.headModel.setTexture(headTexture, 1)

    def cleanupSuit(self):
        self.removeHealthBar()
        if 'body' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['body']
        if self.shadow:
            self.deleteShadow()
        if self.headModel:
            self.headModel.removeNode()
            self.headModel = None
        if self.getPart('body'):
            self.removePart('body')

    def setName(self, nameString, charName):
        Avatar.Avatar.setName(self, nameString, avatarType=self.avatarType, charName=charName, createNow = 1)

    def setupNameTag(self):
        Avatar.Avatar.setupNameTag(self)
        self.nameTag.setText(self.nameTag.getText() + "\nLevel %d" % self.level)

    def setChat(self, chatString):
        self.chat = chatString
        if self.isSkele:
            if "?" in chatString:
                self.suit_dial = base.audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_question.mp3")
            elif "!" in chatString:
                self.suit_dial = base.audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_grunt.mp3")
            else:
                self.suit_dial = base.audio3d.loadSfx("phase_5/audio/sfx/Skel_COG_VO_statement.mp3")
        elif self.head in ["vp"]:
            if "?" in chatString:
                self.suit_dial = base.audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_question.mp3")
            elif "!" in chatString:
                self.suit_dial = base.audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_grunt.mp3")
            else:
                self.suit_dial = base.audio3d.loadSfx("phase_9/audio/sfx/Boss_COG_VO_statement.mp3")
        else:
            if "?" in chatString:
                self.suit_dial = base.audio3d.loadSfx(
                    random.choice(
                        [
                            "phase_3.5/audio/dial/COG_VO_question.mp3",
                            "phase_3.5/audio/dial/COG_VO_question_2.mp3"
                        ]
                    )
                )
            elif "!" in chatString:
                self.suit_dial = base.audio3d.loadSfx("phase_3.5/audio/dial/COG_VO_grunt.mp3")
            else:
                self.suit_dial = base.audio3d.loadSfx("phase_3.5/audio/dial/COG_VO_statement.mp3")
        if self.isSkele:
            base.audio3d.attachSoundToObject(self.suit_dial, self)
        else:
            base.audio3d.attachSoundToObject(self.suit_dial, self.headModel)
        self.suit_dial.play()
        Avatar.Avatar.setChat(self, chatString)

    def generateHealthMeter(self):
        self.removeHealthBar()
        model = loader.loadModel("phase_3.5/models/gui/matching_game_gui.bam")
        button = model.find('**/minnieCircle')
        button.setScale(3.0)
        button.setH(180)
        button.setColor(self.healthColors[0])
        chestNull = self.find('**/def_joint_attachMeter')
        if chestNull.isEmpty():
            chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = loader.loadModel("phase_3.5/models/props/glow.bam")
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.condition = 0
        if hasattr(self, 'getHealth'):
            self.updateHealthBar(self.getHealth())

    def updateHealthBar(self, hp):
        if not self.healthBar:
            return
        if hp > self.health:
            self.health = hp
        #self.health -= hp
        health = 0.0
        try:
            health = float(hp) / float(self.maxHealth)
        except:
            pass
        if health > 0.95:
            condition = 0
        elif health > 0.7:
            condition = 1
        elif health > 0.3:
            condition = 2
        elif health > 0.05:
            condition = 3
        elif health > 0.0:
            condition = 4
        else:
            condition = 5

        if self.condition != condition:
            if condition == 4:
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.taskName('blink-task'))
            elif condition == 5:
                if self.condition == 4:
                    taskMgr.remove(self.taskName('blink-task'))
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.taskName('blink-task'))
            else:
                self.healthBar.setColor(self.healthColors[condition], 1)
                self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
            self.condition = condition

    def __blinkRed(self, task):
        self.healthBar.setColor(self.healthColors[3], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[3], 1)
        if self.condition == 5:
            self.healthBar.setScale(1.17)
        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setColor(self.healthColors[4], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
        if self.condition == 5:
            self.healthBar.setScale(1.0)
        return Task.done

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None
        if self.condition == 4 or self.condition == 5:
            taskMgr.remove(self.taskName('blink-task'))
        self.healthCondition = 0
        return

    def enterOff(self, ts = 0):
        self.anim = None
        return

    def exitOff(self):
        pass

    def exitGeneral(self):
        self.stop()

    def enterFlail(self, ts = 0):
        self.pingpong("flail", fromFrame = 30, toFrame = 35)

    def exitFlail(self):
        self.stop()

    def enterNeutral(self, ts = 0):
        self.show()
        self.timestampAnimTrack = Sequence(Wait(ts), Func(self.loop, "neutral"))
        self.timestampAnimTrack.start()

    def exitNeutral(self):
        self.timestampAnimTrack.pause()
        self.timestampAnimTrack = None
        self.exitGeneral()

    def enterRollodex(self, ts = 0):
        self.play("rollodex")

    def exitRollodex(self):
        self.exitGeneral()

    def enterWalk(self, ts = 0):
        self.show()
        self.timestampAnimTrack = Sequence(Wait(ts), Func(self.loop, "walk"))
        self.timestampAnimTrack.start()
        self.disableShadowRay()

    def exitWalk(self):
        self.timestampAnimTrack.pause()
        self.timestampAnimTrack = None
        self.exitGeneral()
        self.enableShadowRay()

    def __moveSuitUpForDropAnim(self):
        self.getGeomNode().setZ(0.5)

    def __moveSuitDownToNormal(self):
        self.getGeomNode().setZ(0)

    def enterDrop(self, ts = 0):
        self.suitTrack = Parallel(
            ActorInterval(self, 'drop')#,
            #Sequence(Wait(0.1), Func(self.__moveSuitUpForDropAnim), Wait(2.7), Func(self.__moveSuitDownToNormal))
        )
        self.suitTrack.start()

    def exitDrop(self):
        if self.suitTrack:
            self.suitTrack.finish()
            self.suitTrack = None

    def enterDropReact(self, ts = 0):
        self.play('drop-react')

    def exitDropReact(self):
        self.stop()

    def enterSSquirt(self, ts = 0):
        self.play('squirt-small')

    def exitSSquirt(self):
        self.stop()

    def enterLSquirt(self, ts = 0):
        self.play('squirt-large')

    def exitLSquirt(self):
        self.stop()

    def generateLoserSuit(self):
        if not self.isSkele:
            handColor = self.find('**/hands').getColor()
        self.cleanupSuit()
        if self.type == "A":
            if self.isSkele:
                self.loadModel("phase_5/models/char/cogA_robot-lose-mod.bam", 'body')
            else:
                self.loadModel("phase_4/models/char/suitA-lose-mod.bam", 'body')
            self.loadAnims({"lose": "phase_4/models/char/suitA-lose.bam"}, 'body')
        if self.type == "B":
            if self.isSkele:
                self.loadModel("phase_5/models/char/cogB_robot-lose-mod.bam", 'body')
            else:
                self.loadModel("phase_4/models/char/suitB-lose-mod.bam", 'body')
            self.loadAnims({"lose": "phase_4/models/char/suitB-lose.bam"}, 'body')
        if self.type == "C":
            if self.isSkele:
                self.loadModel("phase_5/models/char/cogC_robot-lose-mod.bam", 'body')
            else:
                self.loadModel("phase_3.5/models/char/suitC-lose-mod.bam", 'body')
            self.loadAnims({"lose": "phase_3.5/models/char/suitC-lose.bam"}, 'body')
        if self.isSkele:
            self.find('**/tie').setTexture(self.suit_tie, 1)
            self.setTwoSided(1)
        else:
            self.find('**/hands').setColor(handColor)
            self.find('**/legs').setTexture(self.suit_leg, 1)
            self.find('**/arms').setTexture(self.suit_sleeve, 1)
            self.find('**/torso').setTexture(self.suit_blazer, 1)
        self.generateHead(self.type, self.head)
        self.rescaleSuit()
        self.parentSuitParts()
        self.deleteNameTag()
        Avatar.Avatar.initShadow(self)

    def enterDie(self, ts = 0):
        self.show()
        self.generateLoserSuit()
        self.clearChat()
        self.state = "dead"
        self.play("lose")
        deathSound = base.audio3d.loadSfx("phase_3.5/audio/sfx/Cog_Death_Full.mp3")
        base.audio3d.attachSoundToObject(deathSound, self)
        trackName = self.uniqueName('enterDie')

        smallGears = ParticleLoader.loadParticleEffect('phase_3.5/etc/gearExplosionSmall.ptf')
        smallGears.getParticlesNamed('particles-1').setPoolSize(30)

        singleGear = ParticleLoader.loadParticleEffect('phase_3.5/etc/gearExplosion.ptf')
        singleGear.getParticlesNamed('particles-1').setPoolSize(1)

        smallGearExplosion = ParticleLoader.loadParticleEffect('phase_3.5/etc/gearExplosion.ptf')
        smallGearExplosion.getParticlesNamed('particles-1').setPoolSize(10)

        bigGearExplosion = ParticleLoader.loadParticleEffect('phase_3.5/etc/gearExplosionBig.ptf')
        bigGearExplosion.getParticlesNamed('particles-1').setPoolSize(30)

        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)

        self.smallGears = smallGears
        self.smallGears.setPos(self.find('**/joint_head').getPos() + (0,0, 2))
        self.singleGear = singleGear
        self.smallGearExp = smallGearExplosion
        self.bigGearExp = bigGearExplosion

        gearTrack = Sequence(Wait(0.7), Func(self.doSingleGear), Wait(1.5), Func(self.doSmallGears), Wait(3.0), Func(self.doBigExp))
        self.suitTrack = Parallel(Sequence(Wait(0.7), Func(self.doSingleGear), Wait(4.3),
                Func(self.suitExplode), Wait(1.0), Func(self.delSuit)), gearTrack, name = trackName)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        Sequence(Wait(0.8), SoundInterval(deathSound)).start()
        self.acceptOnce(self.suitTrack.getName(), self.exitDie)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self, trackName)
        self.suitTrack.start(ts)
        del deathSound

    def doSingleGear(self):
        self.singleGear.start(self.getGeomNode())

    def doSmallGears(self):
        self.smallGears.start(self.getGeomNode())

    def doSmallExp(self):
        self.smallGearExp.start(self.getGeomNode())

    def doBigExp(self):
        self.bigGearExp.start(self.getGeomNode())

    def suitExplode(self):
        self.explosion = loader.loadModel("phase_3.5/models/props/explosion.bam")
        self.explosion.setScale(0.5)
        self.explosion.reparentTo(render)
        self.explosion.setBillboardPointEye()
        if self.isSkele:
            self.explosion.setPos(self.getPart("body").find('**/joint_head').getPos(render) + (0, 0, 2))
        else:
            self.explosion.setPos(self.headModel.getPos(render) + (0,0,2))

    def delSuit(self):
        self.disableBodyCollisions()

    def exitDie(self):
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getName())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        if hasattr(self, 'singleGear'):
            self.singleGear.cleanup()
            del self.singleGear
        if hasattr(self, 'smallGears'):
            self.smallGears.cleanup()
            del self.smallGears
        if hasattr(self, 'smallGearExp'):
            self.smallGearExp.cleanup()
            del self.smallGearExp
        if hasattr(self, 'bigGearExp'):
            self.bigGearExp.cleanup()
            del self.bigGearExp
        if self.explosion:
            self.explosion.removeNode()
            self.explosion = None

    def enterFlyNeutral(self, ts = 0):
        self.disableRay()
        self.sfx = base.audio3d.loadSfx("phase_4/audio/sfx/TB_propeller.wav")
        self.prop = Actor("phase_4/models/props/propeller-mod.bam",
                        {"chan": "phase_4/models/props/propeller-chan.bam"})
        base.audio3d.attachSoundToObject(self.sfx, self.prop)
        self.prop.reparentTo(self.find('**/joint_head'))
        self.sfx.setLoop(True)
        self.sfx.play()
        self.prop.loop('chan', fromFrame = 0, toFrame = 3)
        self.setPlayRate(0.8, 'land')
        self.pingpong('land', fromFrame = 0, toFrame = 10)

    def exitFlyNeutral(self):
        self.prop.cleanup()
        del self.prop
        base.audio3d.detachSound(self.sfx)
        del self.sfx
        self.stop()

    def enterFlyDown(self, ts = 0):
        self.disableRay()
        self.fd_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/ENC_propeller_in.mp3")
        self.prop = Actor("phase_4/models/props/propeller-mod.bam",
                        {"chan": "phase_4/models/props/propeller-chan.bam"})
        base.audio3d.attachSoundToObject(self.fd_sfx, self.prop)
        self.prop.reparentTo(self.find('**/joint_head'))
        self.fd_sfx.play()
        dur = self.getDuration('land')
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('enterFlyDown')
        else:
            name = 'enterFlyDown'
        self.suitTrack = Parallel(Sequence(Func(self.pose, 'land', 0), Func(self.prop.loop, 'chan', fromFrame=0, toFrame=3),
                            Wait(1.75),
                            Func(self.prop.play, 'chan', fromFrame=3),
                            Wait(0.15),
                            ActorInterval(self, 'land', duration=dur)), name = name)
        if not self.hasSpawned:
            showSuit = Sequence(Func(self.hideSuit), Wait(0.3), Func(self.showSuit))
            self.hasSpawned = True
            self.suitTrack.append(showSuit)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.exitFlyAway)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self, name)
        self.suitTrack.start(ts)

    def hideSuit(self):
        self.hide()

    def showSuit(self):
        self.show()
        fadeIn = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(0.6, colorScale=Vec4(1,1,1,1), startColorScale=Vec4(1,1,1,0)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, render))
        fadeIn.start()

    def initializeLocalCollisions(self, name):
        self.notify.info('Initializing Local Collisions!')
        Avatar.Avatar.initializeLocalCollisions(self, 1, 3, name)

    def initializeBodyCollisions(self):
        self.notify.info('Initializing Body Collisions!')
        Avatar.Avatar.initializeBodyCollisions(self, self.avatarType, 6, 2)
        self.initializeRay(self.avatarType, 2)
        #self.collTube.setTangible(0)

    def exitFlyDown(self):
        self.initializeRay(self.avatarType, 2)
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        if hasattr(self, 'fd_sfx'):
            base.audio3d.detachSound(self.fd_sfx)
        self.exitGeneral()
        if self.prop:
            self.prop.cleanup()
            self.prop = None

    def enterFlyAway(self, ts = 0):
        self.show()
        self.fa_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/ENC_propeller_out.mp3")
        self.prop = Actor("phase_4/models/props/propeller-mod.bam",
                        {"chan": "phase_4/models/props/propeller-chan.bam"})
        base.audio3d.attachSoundToObject(self.fa_sfx, self.prop)
        self.fa_sfx.play()
        self.prop.reparentTo(self.find('**/joint_head'))
        self.prop.setPlayRate(-1.0, "chan")
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('enterFlyAway')
        else:
            name = 'enterFlyAway'
        self.suitTrack = Sequence(Func(self.prop.play, 'chan', fromFrame=3),
                            Wait(1.75),
                            Func(self.prop.play, 'chan', fromFrame=0, toFrame=3), name = name)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.exitFlyAway)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self, name)
        self.suitTrack.start(ts)
        self.setPlayRate(-1.0, 'land')
        self.play('land')

    def exitFlyAway(self):
        if self.suitTrack:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        if hasattr(self, 'fa_sfx'):
            base.audio3d.detachSound(self.fa_sfx)
        self.exitGeneral()
        if self.prop:
            self.prop.cleanup()
            self.prop = None

    def enterAttack(self, attack, ts = 0):
        self.show()
        """
        self.attack = attack

        self.weapon_state = 'start'

        if attack == "canned":
            self.weapon = loader.loadModel("phase_5/models/props/can.bam")
            self.weapon.setScale(15)
            self.weapon.setR(180)
            self.wss = CollisionSphere(0,0,0,0.05)
        elif attack == "clipontie":
            self.weapon = loader.loadModel("phase_5/models/props/power-tie.bam")
            self.weapon.setScale(4)
            self.weapon.setR(180)
            self.wss = CollisionSphere(0,0,0,0.2)
        elif attack == "sacked":
            self.weapon = loader.loadModel("phase_5/models/props/sandbag-mod.bam")
            self.weapon.setScale(2)
            self.weapon.setR(180)
            self.weapon.setP(90)
            self.weapon.setY(-2.8)
            self.weapon.setZ(-0.3)
            self.wss = CollisionSphere(0,0,0,1)
        elif attack == "playhardball":
            self.weapon = loader.loadModel("phase_5/models/props/baseball.bam")
            self.weapon.setScale(10)
            self.wss = CollisionSphere(0,0,0,0.1)
            self.weapon.setZ(-0.5)
        elif attack == "marketcrash":
            self.weapon = loader.loadModel("phase_5/models/props/newspaper.bam")
            self.weapon.setScale(3)
            self.weapon.setPos(0.41, -0.06, -0.06)
            self.weapon.setHpr(90, 0, 270)
            self.wss = CollisionSphere(0,0,0,0.35)
        elif attack == "glowerpower":
            self.weapon = loader.loadModel("phase_5/models/props/dagger.bam")
            self.wss = CollisionSphere(0,0,0,1)
        else:
            notify.error("unknown attack!")
        self.wss.setTangible(0)

        self.throwObjectId = random.uniform(0, 101010101010)
        if hasattr(self, 'uniqueName'):
            name = self.uniqueName('enterAttack')
        else:
            name = 'enterAttack'
        self.suitTrack = Sequence(name = name)

        if attack == "canned" or attack == "playhardball":
            self.weapon.reparentTo(self.find('**/joint_Rhold'))
            if self.type == "C":
                self.suitTrack.append(Wait(2.3))
            else:
                self.suitTrack.append(Wait(3))
            self.play("throw-object")
        elif attack == "clipontie" or attack == "marketcrash" or attack == "sacked":
            self.weapon.reparentTo(self.find('**/joint_Rhold'))
            if self.type == "C":
                self.suitTrack.append(Wait(2.3))
            else:
                self.suitTrack.append(Wait(3))
            self.play("throw-paper")
        elif attack == "glowerpower":
            self.suitTrack.append(Wait(1))
            self.play("glower")
        self.suitTrack.append(Func(self.throwObject))
        if attack == "glowerpower":
            self.suitTrack.append(Wait(0.5))
        else:
            self.suitTrack.append(Wait(1.0))
        self.suitTrack.append(Func(self.delWeapon))
        self.weaponSensorId = random.uniform(0, 1010101010101001)
        wsnode = CollisionNode('weaponSensor' + str(self.weaponSensorId))
        wsnode.addSolid(self.wss)
        wsnode.setCollideMask(CIGlobals.WallBitmask)
        self.wsnp = self.weapon.attachNewNode(wsnode)
        if attack == "sacked":
            self.wsnp.setZ(1)
        elif attack == "marketcrash":
            self.wsnp.setPos(-0.25, 0.3, 0)
        self.suitTrack.setDoneEvent(self.suitTrack.getName())
        self.acceptOnce(self.suitTrack.getDoneEvent(), self.exitAttack)
        self.suitTrack.delayDelete = DelayDelete.DelayDelete(self, 'enterAttack')
        self.suitTrack.start()
        """

        if hasattr(self, 'uniqueName'):
            doneEvent = self.uniqueName('suitAttackDone')
        else:
            doneEvent = 'suitAttackDone'
        self.suitAttackState = SuitAttacks(doneEvent, self)
        self.suitAttackState.load(attack)
        self.suitAttackState.enter(ts)
        self.acceptOnce(doneEvent, self.handleSuitAttackDone)

    def handleSuitAttackDone(self):
        self.exitAttack()

    def exitAttack(self):
        if hasattr(self, 'uniqueName'):
            self.ignore(self.uniqueName('suitAttackDone'))
        else:
            self.ignore('suitAttackDone')
        if hasattr(self, 'suitAttackState'):
            self.suitAttackState.exit()
        if hasattr(self, 'suitAttackState'):
            self.suitAttackState.unload()
        if hasattr(self, 'suitAttackState'):
            del self.suitAttackState

    def delWeapon(self):
        if self.wtrajectory:
            self.wtrajectory.pause()
            self.wtrajectory = None
        if self.weapon:
            self.weapon.removeNode()
            self.weapon = None

    def interruptAttack(self):
        if hasattr(self, 'suitAttackState'):
            self.suitAttackState.currentAttack.interruptAttack()

    def handleWeaponTouch(self):
        if hasattr(self, 'suitAttackState'):
            self.suitAttackState.currentAttack.handleWeaponTouch()

    def weaponCollisions(self):
        self.wsnp.setCollideMask(BitMask32(0))
        self.wsnp.node().setFromCollideMask(CIGlobals.EventBitmask)

        event = CollisionHandlerEvent()
        event.setInPattern("%fn-into")
        event.setOutPattern("%fn-out")
        base.cTrav.addCollider(self.wsnp, event)

    def throwObject(self):
        self.playWeaponSound()

        self.weaponNP = NodePath("weaponNP")
        try: self.weaponNP.reparentTo(self)
        except: return
        self.weaponNP.setScale(render, 1.0)
        self.weaponNP.setPos(0, 50, 0)
        self.weaponNP.setHpr(0, 0, 0)

        if self.weapon:
            self.weapon.setScale(self.weapon.getScale(render))
        try: self.weapon.reparentTo(render)
        except: return

        self.weapon.setPos(0,0,0)
        self.weapon.setHpr(0,0,0)

        if self.attack == "glowerpower":
            self.weapon.setH(self.weaponNP.getH(render))
            self.wtrajectory = self.weapon.posInterval(0.5,
                                        Point3(self.weaponNP.getPos(render)),
                                        startPos=(self.getX(render), self.getY(render) + 3, self.find('**/joint_head').getZ(render)))
            self.wtrajectory.start()
        else:
            self.wtrajectory = ProjectileInterval(self.weapon,
                                        startPos = (self.find('**/joint_Rhold').getPos(render)),
                                        endPos = self.weaponNP.getPos(render),
                                        gravityMult = 0.7, duration = 1)
            self.wtrajectory.start()
        self.weapon_state = 'released'

    def playWeaponSound(self):
        if self.attack == "glowerpower":
            self.weapon_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_glower_power.mp3")
        elif self.attack == "canned":
            self.weapon_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_canned_tossup_only.mp3")
        elif self.attack == "clipontie":
            self.weapon_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_powertie_throw.mp3")
        elif self.attack == "sacked":
            self.weapon_sfx = None
        elif self.attack == "playhardball":
            self.weapon_sfx = base.audio3d.loadSfx("phase_5/audio/sfx/SA_hardball_throw_only.mp3")
        elif self.attack == "marketcrash":
            self.weapon_sfx = None
        if self.weapon and self.weapon_sfx:
            base.audio3d.attachSoundToObject(self.weapon_sfx, self.weapon)
            self.weapon_sfx.play()

    """
    def exitAttack(self):
        if self.suitTrack != None:
            self.ignore(self.suitTrack.getDoneEvent())
            self.suitTrack.finish()
            DelayDelete.cleanupDelayDeletes(self.suitTrack)
            self.suitTrack = None
        if self.wtrajectory:
            self.wtrajectory.pause()
            self.wtrajectory = None
        if self.weapon:
            self.weapon.removeNode()
            self.weapon = None
        if hasattr(self, 'weaponNP'):
            self.weaponNP.removeNode()
            del self.weaponNP
    """

    def enterPie(self, ts = 0):
        self.show()
        self.play("pie")

    def exitPie(self):
        self.exitGeneral()

    def enterWin(self, ts = 0):
        self.play("win")

    def exitWin(self):
        self.exitGeneral()

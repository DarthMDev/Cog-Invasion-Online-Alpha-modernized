# Filename: DistributedNPCToon.py
# Created by:  blach (31Jul15)

from panda3d.core import CollisionNode, CollisionSphere, BitMask32
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, LerpPosInterval, LerpQuatInterval

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quests import Quests
from DistributedToon import DistributedToon

class DistributedNPCToon(DistributedToon):
    notify = directNotify.newCategory("DistributedNPCToon")

    def __init__(self, cr):
        DistributedToon.__init__(self, cr)
        self.collisionNodePath = None
        self.cameraTrack = None
        self.originIndex = None
        self.npcId = None
        self.currentChatIndex = 0

    def setNpcId(self, id):
        self.npcId = id

    def getNpcId(self):
        return self.npcId

    def setOriginIndex(self, index):
        self.originIndex = index

    def getOriginIndex(self):
        return self.originIndex

    def __setupCollisions(self):
        sphere = CollisionSphere(0, 0, 0, 4)
        sphere.setTangible(0)
        collisionNode = CollisionNode(self.uniqueName('NPCToonSphere'))
        collisionNode.addSolid(sphere)
        collisionNode.setCollideMask(CIGlobals.WallBitmask)
        self.collisionNodePath = self.attachNewNode(collisionNode)
        self.collisionNodePath.setY(1.5)

    def __removeCollisions(self):
        if self.collisionNodePath:
            self.collisionNodePath.removeNode()
            self.collisionNodePath = None

    def handleEnterCollision(self, entry):
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.stopSmartCamera()
        self.sendUpdate('requestEnter', [])

    def doCameraNPCInteraction(self):
        currCamPos = camera.getPos()
        currCamHpr = camera.getHpr()
        camera.setX(camera.getX() + 5)
        camera.setY(camera.getY() + 5)
        camera.headsUp(self)
        newCamPos = camera.getPos()
        newCamHpr = camera.getHpr()
        camera.setPos(currCamPos)
        camera.setHpr(currCamHpr)

        self.cameraTrack = Parallel(
            LerpPosInterval(camera, duration = 1.0, pos = newCamPos, startPos = currCamPos, blendType = 'easeOut'),
            LerpQuatInterval(camera, duration = 1.0, quat = newCamHpr, startHpr = currCamHpr, blendType = 'easeOut')
        )
        self.cameraTrack.start()

    def stopCameraTrack(self):
        if self.cameraTrack:
            self.cameraTrack.finish()
            self.cameraTrack = None

    def enterAccepted(self):
        self.doCameraNPCInteraction()
        questId, quest = base.localAvatar.questManager.getQuestAndIdWhereCurrentObjectiveIsToVisit(self.npcId)
        self.currentQuestObjective = quest.currentObjectiveIndex
        self.currentQuestId = questId
        self.doNPCChat()

    def doNPCChat(self):
        self.b_setChat(Quests.QuestNPCDialogue[self.currentQuestId][self.currentQuestObjective][self.currentChatIndex])
        self.currentChatIndex += 1
        self.acceptOnce('mouse1-up', self.doNextNPCChat)

    def doNextNPCChat(self):
        if self.currentChatIndex >= len(Quests.QuestNPCDialogue[self.currentQuestId][self.currentQuestObjective]):
            self.sendUpdate('requestExit', [])
        else:
            self.doNPCChat()

    def rejectEnter(self):
        self.exitAccepted()

    def exitAccepted(self):
        self.stopCameraTrack()
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptCollisions()

    def acceptCollisions(self):
        self.acceptOnce('enter' + self.uniqueName('NPCToonSphere'), self.handleEnterCollision)

    def ignoreCollisions(self):
        self.ignore('enter' + self.uniqueName('NPCToonSphere'))

    def __npcOriginPoll(self, task):
        if task.time > 4.0:
            self.notify.warning("Giving up waiting for npc origin after %d seconds. Will parent to render." % task.time)
            self.reparentTo(render)
            return task.done
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            return task.done
        return task.cont

    def startNPCOriginPoll(self):
        base.taskMgr.add(self.__npcOriginPoll, self.uniqueName('NPCOriginPoll'))

    def stopNPCOriginPoll(self):
        base.taskMgr.remove(self.uniqueName('NPCOriginPoll'))

    def announceGenerate(self):
        DistributedToon.announceGenerate(self)
        self.startLookAround()
        self.__setupCollisions()
        npcOrigin = render.find('**/npc_origin_' + str(self.originIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
        else:
            self.startNPCOriginPoll()
        self.acceptCollisions()

    def disable(self):
        self.ignore('mouse1-up')
        self.stopLookAround()
        self.stopNPCOriginPoll()
        self.originIndex = None
        self.npcId = None
        self.stopCameraTrack()
        self.ignoreCollisions()
        self.__removeCollisions()
        DistributedToon.disable(self)

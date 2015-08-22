# Filename: Quests.py
# Created by:  blach (30Jul15)

from lib.coginvasion.globals.CIGlobals import *

Any = 0

DefeatCog = 1
DefeatCogDept = 2
DefeatCogInvasion = 3
DefeatCogTournament = 4
DefeatCogLevel = 11
VisitNPC = 5
VisitHQOfficer = 12

DefeatCogObjectives = [DefeatCog, DefeatCogDept, DefeatCogLevel]
DefeatObjectives = [DefeatCog, DefeatCogDept, DefeatCogInvasion, DefeatCogTournament, DefeatCogLevel]

RewardNone = 6
RewardGagTrackProgress = 7
RewardJellybeans = 8
RewardHealth = 9
RewardAccess = 10

TierTT = 13
TierDD = 14
TierDG = 15
TierML = 16
TierBR = 17
TierDL = 18

Quests = {
    #0: {"objectives": [[DefeatCogLevel, 1, 3, Any]], "reward": (RewardHealth, 1), "tier": TierTT},
    #1: {"objectives": [[VisitNPC, 'visitanNPC', 2308, 2801], []]}
    0: {"objectives": [[VisitNPC, 'visitanNPC', 2322, 2653],
                    [DefeatCog, 'namedropper', 10, ToontownCentralId],
                    [VisitNPC, 'visitanNPC', 2322, 2653]],
        "reward": (RewardHealth, 3), "tier": TierTT},
    1: {"objectives": [[DefeatCogDept, 'c', 5, Any], [VisitHQOfficer, 'visHQ', 0, 0]], "reward": (RewardHealth, 2), "tier": TierTT},
    2: {"objectives": [[VisitNPC, 'visitanNPC', 2003, 2516],
                    [DefeatCogDept, 'm', 4, Any],
                    [VisitNPC, 'visitanNPC', 2003, 2516]],
        "reward": (RewardHealth, 1), "tier": TierTT}
}

QuestNPCDialogue = {

}

QuestHQOfficerDialogue = {}

HQOfficerQuestCongrats = "Nice job completing that Quest! You have earned your reward."

DefeatText = "Defeat"
VisitText = "Visit"

class Objective:

    def __init__(self, objectiveArgs, progress):
        self.objectiveArgs = objectiveArgs
        self.type = objectiveArgs[0]
        if self.type == DefeatCogLevel:
            self.minCogLevel = objectiveArgs[1]
        else:
            self.subject = objectiveArgs[1]
        if self.type == VisitNPC:
            self.npcId = objectiveArgs[2]
            self.npcZone = objectiveArgs[3]
        else:
            self.goal = objectiveArgs[2]
            self.area = objectiveArgs[3]
        self.progress = progress

    def isComplete(self):
        return self.progress >= self.goal

class Quest:

    def __init__(self, questId, currentObjectiveIndex, currentObjectiveProgress, index):
        self.questId = questId
        self.numObjectives = len(Quests[questId]["objectives"])
        self.currentObjectiveIndex = currentObjectiveIndex
        self.currentObjectiveProgress = currentObjectiveProgress
        objArgs = Quests[questId]["objectives"][currentObjectiveIndex]
        self.currentObjective = Objective(objArgs, currentObjectiveProgress)
        rewardData = Quests[questId]["reward"]
        self.rewardType = rewardData[0]
        self.rewardValue = rewardData[1]
        self.index = index
        self.tier = Quests[questId]["tier"]
        self.lastQuestInTier = Quests[questId].get("lastQuestInTier", False)

    def isLastQuestInTier(self):
        return self.lastQuestInTier

    def getTier(self):
        return self.tier

    def isComplete(self):
        if self.currentObjective.type != VisitNPC:
            if self.currentObjective.isComplete() and self.currentObjectiveIndex >= self.numObjectives - 1:
                return True
        else:
            return self.currentObjectiveIndex >= self.numObjectives - 1

    def getCurrentObjectiveProgress(self):
        return self.currentObjectiveProgress

    def getNumObjectives(self):
        return self.numObjectives

    def getCurrentObjective(self):
        return self.currentObjective

    def getCurrentObjectiveIndex(self):
        return self.currentObjectiveIndex

    def getRewardType(self):
        return self.rewardType

    def getRewardValue(self):
        return self.rewardValue

    def getReward(self):
        return [self.rewardType, self.rewardValue]

    def getIndex(self):
        return self.index

    def cleanup(self):
        self.questId = None
        self.numObjectives = None
        self.currentObjectiveIndex = None
        self.currentObjectiveProgress = None
        self.currentObjective = None
        self.rewardType = None
        self.rewardValue = None
        self.index = None
        self.tier = None

"""

  Filename: SuitBank.py
  Created by: DecodedLogic (01Sep15)

"""

from lib.coginvasion.cog import SuitGlobals
from lib.coginvasion.cog.SuitType import SuitType
from lib.coginvasion.cog import Dept
from lib.coginvasion.cog.Head import Head
from lib.coginvasion.cog.SuitPanicBehavior import SuitPanicBehavior
from lib.coginvasion.cog import Voice
from lib.coginvasion.cog import SuitAttacks
from panda3d.core import VBase4

class SuitPlan:
    
    def __init__(self, name, suitType, dept, head, scale, nametagZ, headColor = None, 
                 headTex = None, headAnims = None, handColor = None, forcedVariant = None, forcedVoice = None, 
                 levelRange = None, forcedLevel = None, attacks = SuitAttacks.SuitAttackLengths.keys()):
        self.name = name
        self.suitType = suitType
        self.dept = dept
        self.scale = scale
        self.nametagZ = nametagZ
        self.handColor = handColor
        self.forcedVariant = forcedVariant
        self.forcedVoice = forcedVoice
        self.attacks = attacks
        self.levelRange = levelRange
        self.forcedLevel = forcedLevel
        self.behaviors = []
        
        if 'phase' in head:
            self.head = Head(None, head, headColor = headColor, headTex = headTex, headAnims = headAnims)
        else:
            self.head = Head(self.suitType, head, headColor = headColor, headTex = headTex)
        
        if not self.handColor:
            self.handColor = self.dept.getHandColor()
        if not len(self.behaviors):
            defaultBehaviors = [[SuitPanicBehavior, 4]]
            self.behaviors = defaultBehaviors
            
    def getName(self):
        return self.name
    
    def getSuitType(self):
        return self.suitType
            
    def getDept(self):
        return self.dept
    
    def getHead(self):
        return self.head
    
    def getScale(self):
        return self.scale
    
    def getNametagZ(self):
        return self.nametagZ
    
    def getHandColor(self):
        return self.handColor
    
    def getForcedVariant(self):
        return self.forcedVariant
    
    def getForcedVoice(self):
        return self.forcedVoice
    
    def getAttacks(self):
        return self.attacks
    
    def getLevelRange(self):
        return self.levelRange
    
    def getForcedLevel(self):
        return self.forcedLevel
    
    def getBehaviors(self):
        return self.behaviors

TheBigCheese = SuitPlan(
    SuitGlobals.TheBigCheese, 
    SuitType.A, 
    Dept.BOSS, 
    'bigcheese',
    scale = 7.0,
    nametagZ = 9.8,
    handColor = VBase4(0.75, 0.95, 0.75, 1.0),
    levelRange = (8, 12)
)
CorporateRaider = SuitPlan(
    SuitGlobals.CorporateRaider,
    SuitType.C,
    Dept.BOSS,
    'tightwad',
    scale = 6.75,
    nametagZ = 9.0,
    handColor = VBase4(0.85, 0.55, 0.55, 1.0),
    headTex = 'phase_3.5/maps/corporate-raider.jpg',
    levelRange = (7, 11)
)
HeadHunter = SuitPlan(
    SuitGlobals.HeadHunter,
    SuitType.A,
    Dept.BOSS,
    'headhunter',
    scale = 6.5,
    nametagZ = 7.9,
    levelRange = (6, 10)
)
Downsizer = SuitPlan(
    SuitGlobals.Downsizer,
    SuitType.B,
    Dept.BOSS,
    'beancounter',
    scale = 4.5,
    nametagZ = 6.3,
    levelRange = (5, 9)
)
Micromanager = SuitPlan(
    SuitGlobals.Micromanager,
    SuitType.C,
    Dept.BOSS,
    'micromanager',
    scale = 2.5,
    nametagZ = 3.5,
    levelRange = (4, 8)
)
Yesman = SuitPlan(
    SuitGlobals.Yesman,
    SuitType.A,
    Dept.BOSS,
    'yesman',
    scale = 4.125,
    nametagZ = 5.6,
    levelRange = (3, 7)
)
PencilPusher = SuitPlan(
    SuitGlobals.PencilPusher,
    SuitType.B,
    Dept.BOSS,
    'pencilpusher',
    scale = 3.35,
    nametagZ = 5.2,
    levelRange = (2, 6)
)
Flunky = SuitPlan(
    SuitGlobals.Flunky,
    SuitType.C,
    Dept.BOSS,
    'flunky',
    scale = 4.0,
    nametagZ = 5.2,
    levelRange = (1, 5)
)
BigWig = SuitPlan(
    SuitGlobals.BigWig,
    SuitType.A,
    Dept.LAW,
    'bigwig',
    scale = 7.0,
    nametagZ = 9.2,
    levelRange = (8, 12)
)
LegalEagle = SuitPlan(
    SuitGlobals.LegalEagle,
    SuitType.A,
    Dept.LAW,
    'legaleagle',
    scale = 7.125,
    nametagZ = 8.75,
    handColor = VBase4(0.25, 0.25, 0.5, 1.0),
    levelRange = (7, 11)
)
SpinDoctor = SuitPlan(
    SuitGlobals.SpinDoctor,
    SuitType.B,
    Dept.LAW,
    'telemarketer',
    scale = 5.65,
    nametagZ = 8.3,
    headTex = 'phase_4/maps/spin-doctor.jpg',
    handColor = VBase4(0.5, 0.8, 0.75, 1.0),
    levelRange = (6, 10)
)
BackStabber = SuitPlan(
    SuitGlobals.BackStabber,
    SuitType.A,
    Dept.LAW,
    'backstabber',
    scale = 4.5,
    nametagZ = 7.0,
    levelRange = (5, 9)
)
AmbulanceChaser = SuitPlan(
    SuitGlobals.AmbulanceChaser,
    SuitType.B,
    Dept.LAW,
    'ambulancechaser',
    scale = 4.35,
    nametagZ = 7.0,
    levelRange = (4, 8)
)
DoubleTalker = SuitPlan(
    SuitGlobals.DoubleTalker,
    SuitType.A,
    Dept.LAW,
    'twoface',
    headTex = 'phase_4/maps/double-talker.jpg',
    scale = 4.25,
    nametagZ = 6.0,
    levelRange = (3, 7)
)
Bloodsucker = SuitPlan(
    SuitGlobals.Bloodsucker,
    SuitType.B,
    Dept.LAW,
    'movershaker',
    headTex = 'phase_3.5/maps/bloodsucker.jpg',
    scale = 4.375,
    nametagZ = 6.5,
    handColor = VBase4(0.95, 0.95, 1.0, 1.0),
    levelRange = (2, 6)
)
BottomFeeder = SuitPlan(
    SuitGlobals.BottomFeeder,
    SuitType.C,
    Dept.LAW,
    'tightwad',
    headTex = 'phase_3.5/maps/bottom-feeder.jpg',
    scale = 4.0,
    nametagZ = 5.1,
    levelRange = (1, 5)
)
RobberBaron = SuitPlan(
    SuitGlobals.RobberBaron,
    SuitType.A,
    Dept.CASH,
    'yesman',
    headTex = 'phase_3.5/maps/robberbaron.jpg',
    scale = 7.0,
    nametagZ = 9.4,
    levelRange = (8, 12)
)
LoanShark = SuitPlan(
    SuitGlobals.LoanShark,
    SuitType.B,
    Dept.CASH,
    'loanshark',
    scale = 6.5,
    nametagZ = 8.9,
    handColor = VBase4(0.5, 0.85, 0.75, 1.0),
    levelRange = (7, 11)
)
MoneyBags = SuitPlan(
    SuitGlobals.MoneyBags,
    SuitType.C,
    Dept.CASH,
    'moneybags',
    scale = 5.3,
    nametagZ = 7.4,
    levelRange = (6, 10)
)
NumberCruncher = SuitPlan(
    SuitGlobals.NumberCruncher,
    SuitType.A,
    Dept.CASH,
    'numbercruncher',
    scale = 5.25,
    nametagZ = 7.8,
    levelRange = (5, 9)
)
BeanCounter = SuitPlan(
    SuitGlobals.BeanCounter,
    SuitType.B,
    Dept.CASH,
    'beancounter',
    scale = 4.4,
    nametagZ = 6.3,
    levelRange = (4, 8)
)
Tightwad = SuitPlan(
    SuitGlobals.Tightwad,
    SuitType.C,
    Dept.CASH,
    'tightwad',
    scale = 4.5,
    nametagZ = 5.8,
    levelRange = (3, 7)
)
PennyPincher = SuitPlan(
    SuitGlobals.PennyPincher,
    SuitType.A,
    Dept.CASH,
    'pennypincher',
    scale = 3.55,
    nametagZ = 5.6,
    handColor = VBase4(1.0, 0.5, 0.6, 1.0),
    levelRange = (2, 6)
)
ShortChange = SuitPlan(
    SuitGlobals.ShortChange,
    SuitType.C,
    Dept.CASH,
    'coldcaller',
    scale = 3.6,
    nametagZ = 4.9,
    levelRange = (1, 5)
)
MrHollywood = SuitPlan(
    SuitGlobals.MrHollywood,
    SuitType.A,
    Dept.SALES,
    'yesman',
    scale = 7.0,
    nametagZ = 9.4,
    levelRange = (8, 12)
)
TheMingler = SuitPlan(
    SuitGlobals.TheMingler,
    SuitType.A,
    Dept.SALES,
    'twoface',
    scale = 5.75,
    nametagZ = 8.0,
    headTex = 'phase_3.5/maps/mingler.jpg',
    levelRange = (7, 11)
)
TwoFace = SuitPlan(
    SuitGlobals.TwoFace,
    SuitType.A,
    Dept.SALES,
    'twoface',
    scale = 5.25,
    nametagZ = 7.3,
    levelRange = (6, 10)
)
MoverShaker = SuitPlan(
    SuitGlobals.MoverShaker,
    SuitType.B,
    Dept.SALES,
    'movershaker',
    scale = 4.75,
    nametagZ = 7.1,
    levelRange = (5, 9)
)
GladHander = SuitPlan(
    SuitGlobals.GladHander,
    SuitType.C,
    Dept.SALES,
    'gladhander',
    scale = 4.75,
    nametagZ = 6.7,
    levelRange = (4, 8)
)
NameDropper = SuitPlan(
    SuitGlobals.NameDropper,
    SuitType.A,
    Dept.SALES,
    'numbercruncher',
    scale = 4.35,
    nametagZ = 6.3,
    headTex = 'phase_3.5/maps/namedropper.jpg',
    levelRange = (3, 7)
)
Telemarketer = SuitPlan(
    SuitGlobals.Telemarketer,
    SuitType.B,
    Dept.SALES,
    'telemarketer',
    scale = 3.75,
    nametagZ = 5.6,
    levelRange = (2, 6)
)
ColdCaller = SuitPlan(
    SuitGlobals.ColdCaller,
    SuitType.C,
    Dept.SALES,
    'coldcaller',
    scale = 3.5,
    nametagZ = 4.9,
    headColor = VBase4(0.25, 0.35, 1.0, 1.0),
    handColor = VBase4(0.55, 0.65, 1.0, 1.0),
    levelRange = (1, 5)
)
# Bosses:
VicePresident = SuitPlan(
    SuitGlobals.VicePresident,
    SuitType.A,
    Dept.SALES,
    'phase_9/models/char/sellbotBoss-head-zero.bam',
    headAnims = {'neutral': 'phase_9/models/char/bossCog-head-Ff_neutral.bam'},
    scale = 10.0,
    nametagZ = 14.0,
    levelRange = (70, 70),
    forcedVoice = Voice.BOSS
)
LucyCrossbill = SuitPlan(
    SuitGlobals.LucyCrossbill,
    SuitType.A,
    Dept.LAW,
    'legaleagle',
    scale = 7.125,
    nametagZ = 8.75,
    handColor = VBase4(0.25, 0.25, 0.5, 1.0),
    levelRange = (12, 12)
)

SuitIds = {
    0 : Flunky, 
    1 : PencilPusher, 
    2 : Yesman, 
    3 : Micromanager, 
    4 : Downsizer,
    5 : HeadHunter,
    6 : CorporateRaider,
    7 : TheBigCheese,
    8 : BottomFeeder,
    9 : Bloodsucker,
    10 : DoubleTalker,
    11 : AmbulanceChaser,
    12 : BackStabber,
    13 : SpinDoctor,
    14 : LegalEagle,
    15 : BigWig,
    16 : ShortChange,
    17 : PennyPincher,
    18 : Tightwad,
    19 : BeanCounter,
    20 : NumberCruncher,
    21 : MoneyBags,
    22 : LoanShark,
    23 : RobberBaron,
    24 : ColdCaller,
    25 : Telemarketer,
    26 : NameDropper,
    27 : GladHander,
    28 : MoverShaker,
    29 : TwoFace,
    30 : TheMingler,
    31 : MrHollywood,
    32 : VicePresident,
    33 : LucyCrossbill
}

totalSuits = SuitIds.values()

def getSuitById(suitId):
    return SuitIds.get(suitId)

def getIdFromSuit(suit):
    for suitId, iSuit in SuitIds.items():
        if iSuit == suit:
            return suitId
        
def getSuitByName(suitName):
    for suit in SuitIds.values():
        if suit.getName() == suitName:
            return suit

def getSuits():
    return totalSuits
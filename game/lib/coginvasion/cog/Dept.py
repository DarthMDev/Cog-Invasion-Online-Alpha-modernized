"""

  Filename: Dept.py
  Created by: DecodedLogic (31July14)

"""

from panda3d.core import VBase4

class Dept:
    
    def __init__(self, name, handColor, tieName, clothPrefix):
        self.name = name
        self.handColor = handColor
        self.tieName = tieName
        self.clothPrefix = clothPrefix
        
    def getHandColor(self):
        return self.handColor
    
    def getTie(self):
        return self.tieName
    
    def getClothingPrefix(self):
        return self.clothPrefix
    
    def getName(self):
        return self.name

BOSS = Dept('Bossbot', VBase4(0.95, 0.75, 0.75, 1), 'boss', 'c')
LAW = Dept('Lawbot', VBase4(0.75, 0.75, 0.95, 1.0), 'legal', 'l')
CASH = Dept('Cashbot', VBase4(0.65, 0.95, 0.85, 1.0), 'money', 'm')
SALES = Dept('Sellbot', VBase4(0.95, 0.75, 0.95, 1.0), 'sales', 's')
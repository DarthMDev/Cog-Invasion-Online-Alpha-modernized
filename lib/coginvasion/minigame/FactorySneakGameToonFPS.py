"""

  Filename: FactorySneakGameToonFPS.py
  Created by: blach (30Mar15)

"""

import ToonFPS
from FactorySneakGameBullet import FactorySneakGameBullet

class FactorySneakGameToonFPS(ToonFPS.ToonFPS):
    
    def __init__(self, mg):
        ToonFPS.ToonFPS.__init__(self, mg)
        
    def enterShoot(self):
        ToonFPS.ToonFPS.enterShoot(self)
        FactorySneakGameBullet(self.mg, self.pistol.find('**/joint_nozzle'), 1)
        self.mg.d_gunShot()
        
    def damageTaken(self, amount, avId):
        self.hp -= amount
        ToonFPS.ToonFPS.damageTaken(self, amount, avId)

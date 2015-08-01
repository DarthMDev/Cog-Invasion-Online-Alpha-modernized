"""

  Filename: GunGameToonFPS.py
  Created by: blach (30Mar15)

"""

import ToonFPS
from GunGameBullet import GunGameBullet
from direct.distributed.ClockDelta import globalClockDelta

class GunGameToonFPS(ToonFPS.ToonFPS):
    
    def __init__(self, mg, weaponName = "pistol"):
        self.kills = 0
        self.deaths = 0
        self.points = 0
        ToonFPS.ToonFPS.__init__(self, mg, weaponName)
        
    def resetStats(self):
        self.points = 0
        self.kills = 0
        self.deaths = 0
        self.gui.updateStats()
        
    def enterAlive(self):
        ToonFPS.ToonFPS.enterAlive(self)
        pos, hpr = self.mg.pickSpawnPoint()
        base.localAvatar.setPos(pos)
        base.localAvatar.setHpr(hpr)
        base.localAvatar.d_broadcastPositionNow()
        if self.mg.fsm.getCurrentState().getName() == "play":
            self.mg.sendUpdate("respawnAvatar", [base.localAvatar.doId])
            
    def enterDead(self, killer):
        self.deaths += 1
        self.updatePoints()
        self.gui.updateStats()
        self.mg.getMyRemoteAvatar().fsm.request('die', [0])
        ToonFPS.ToonFPS.enterDead(self, killer)
    
    def doFreezeCam(self):
        ToonFPS.ToonFPS.doFreezeCam(self)
        taskMgr.doMethodLater(
            3.0,
            self.respawnAfterDeathTask,
            "respawnAfterDeath"
        )
		
    def respawnAfterDeathTask(self, task):
        self.fsm.request('alive')
        return task.done
        
    def exitDead(self):
        taskMgr.remove("respawnAfterDeath")
        ToonFPS.ToonFPS.exitDead(self)
        self.mg.getMyRemoteAvatar().exitDead()
        self.mg.getMyRemoteAvatar().fsm.requestFinalState()
        
    def cleanup(self):
        taskMgr.remove("respawnAfterDeath")
        self.kills = None
        self.deaths = None
        self.points = None
        ToonFPS.ToonFPS.cleanup(self)
        
    def damageTaken(self, amount, avId):
        # We can't die more than once!
        if self.fsm.getCurrentState().getName() == "dead" and self.hp <= 0:
            return
        self.hp -= amount
        if self.fsm.getCurrentState().getName() != "dead" and self.hp <= 0:
            self.mg.sendUpdate('dead', [avId])
        if self.hp <= 0.0:
            timestamp = globalClockDelta.getFrameNetworkTime()
            self.mg.sendUpdate("deadAvatar", [base.localAvatar.doId, timestamp])
        ToonFPS.ToonFPS.damageTaken(self, amount, avId)
            
    def killedSomebody(self):
        self.kills += 1
        self.updatePoints()
        self.gui.updateStats()
        
    def enterShoot(self):
        ToonFPS.ToonFPS.enterShoot(self)
        if self.weaponName == "pistol":
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 1, self.weaponName)
        elif self.weaponName == "shotgun":
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 1, self.weaponName)
            GunGameBullet(self.mg, self.weapon.find('**/joint_nozzle'), 1, self.weaponName)
        self.mg.d_gunShot()

# Filename: SuitUtils.py
# Created by:  blach (29Dec15)

from direct.distributed.ClockDelta import globalClockDelta

import SuitAttacks

import random

def attack(suit, toon, attackIndex = None):
    suit.b_setAnimState('neutral')
    suit.headsUp(toon)
    if attackIndex is None:
        attack = random.choice(suit.suitPlan.getAttacks())
        attackIndex = SuitAttacks.SuitAttackLengths.keys().index(attack)
    else:
        attack = SuitAttacks.SuitAttackLengths.keys()[attackIndex]
    timestamp = globalClockDelta.getFrameNetworkTime()
    if suit.isDead():
        return None
    suit.sendUpdate('doAttack', [attackIndex, toon.doId, timestamp])
    return attack

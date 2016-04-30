# Filename: GunGameGlobals.py
# Created by:  blach (05Aug15)

from TeamMinigame import TEAM1, TEAM2

class GameModes:
    CASUAL = 0
    CTF = 1

class Teams:
    BLUE = TEAM1
    RED = TEAM2

CTF = "Capture the Flag"
CASUAL = "Casual Mode"
RED = "Red Robber Barons"
BLUE = "Blue Bloodsuckers"
MSG_CHOSE_MODE_TIE = "It's a tie! Randomly chose: {0}"
MSG_CHOSE_MODE = "{0}, it is!"

GameModeNameById = {GameModes.CASUAL: CASUAL, GameModes.CTF: CTF}
TeamColorById = {Teams.RED: (1, 0, 0, 1), Teams.BLUE: (0.2, 0.2, 1, 1)}
TeamNameById = {Teams.RED: RED, Teams.BLUE: BLUE}

CTF_SCORE_CAP = 3

ToonSpeedFactor = 1.35
ToonForwardSpeed = 16.0 * ToonSpeedFactor
ToonJumpForce = 24.0
ToonReverseSpeed = 8.0 * ToonSpeedFactor
ToonRotateSpeed = 80.0 * ToonSpeedFactor

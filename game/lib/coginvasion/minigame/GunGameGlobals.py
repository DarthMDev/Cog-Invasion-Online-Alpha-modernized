# Filename: GunGameGlobals.py
# Created by:  blach (05Aug15)

class GameModes:
    CASUAL = 0
    CTF = 1

class Teams:
    RED = 0
    BLUE = 1

CTF = "Capture the Flag"
CASUAL = "Casual Mode"
RED = "Red Robber Barons"
BLUE = "Blue Bloodsuckers"
MSG_WELCOME = "Welcome to the {0}!"
MSG_CHOSE_MODE_TIE = "It's a tie! Randomly chose: {0}"
MSG_CHOSE_MODE = "{0}, it is!"

GameModeNameById = {GameModes.CASUAL: CASUAL, GameModes.CTF: CTF}
TeamColorById = {Teams.RED: (1, 0, 0, 1), Teams.BLUE: (0.2, 0.2, 1, 1)}
TeamNameById = {Teams.RED: RED, Teams.BLUE: BLUE}

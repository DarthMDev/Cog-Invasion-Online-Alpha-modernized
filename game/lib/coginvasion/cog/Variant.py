"""

  Filename: Variant.py
  Created by: DecodedLogic (31July14)

"""


NORMAL, SKELETON, WAITER, MINIGAME = range(4)

def getVariantById(index):
    variants = [NORMAL, SKELETON, WAITER, MINIGAME]
    return variants[index]
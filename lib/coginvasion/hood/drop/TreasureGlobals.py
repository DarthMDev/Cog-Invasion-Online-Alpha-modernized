"""

  Filename: TreasureGlobals.py
  Created by: DecodedLogic (15Jul15)

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.DistributedTTCTreasureAI import DistributedTTCTreasureAI
from lib.coginvasion.hood.DistributedTBTreasureAI import DistributedTBTreasureAI

TreasureTT = 0
TreasureTB = 1

treasureSpawns = {
    CIGlobals.ToontownCentralId : (DistributedTTCTreasureAI, 3, [
            (-60.976, -8.866, 1.3),
            (-90.632, -5.828, -0.63),
            (27.1, -93.5, 2.5),
            (94.2, 33.5, 4),
            (31.554, 56.915, 4),
            (67.1, 105.5, 2.5),
            (-99.15, -87.3407, 0.52499),
            (8.183, -127.016, 3.025),
            (39.684, -80.356, 2.525),
            (129.137, -61.9039, 2.525),
            (92.99, -158.399, 3.025),
            (111.749, -8.59927, 4.57466),
            (37.983, -26.281, 4.025),
            (31.0649, -43.9149, 4.025),
            (10.0156, 105.218, 2.525),
            (46.9667, 169.143, 3.025),
            (100.68, 93.9896, 2.525),
            (129.285, 58.6107, 2.525),
            (-28.6272, 85.9833, 0.525),
            (-111.589, 79.414, 0.525),
            (-136.296, 32.794, 0.525),
    ], 10, 5),
    CIGlobals.TheBrrrghId: (
        DistributedTBTreasureAI, 12,
        [
            (-108, 46, 6.2),
            (-111, 74, 6.2),
            (-126, 81, 6.2),
            (-74, -75, 3.0),
            (-136, -51, 3.0),
            (-20, 35, 6.2),
            (-55, 109, 6.2),
            (58, -57, 6.2),
            (-42, -134, 6.2),
            (-68, -148, 6.2),
            (-1, -62, 6.2),
            (25, 2, 6.2),
            (-133, 53, 6.2),
            (-99, 86, 6.2),
            (30, 63, 6.2),
            (-147, 3, 6.2),
            (-135, -102, 6.2),
            (35, -98, 6.2),
        ],
        10, # Rate
        2 # Maximum
    )
}

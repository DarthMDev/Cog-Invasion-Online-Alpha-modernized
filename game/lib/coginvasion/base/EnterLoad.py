"""

  Filename: EnterLoad.py
  Created by: blach (18Apr15)

"""

from panda3d.core import VirtualFileSystem, Filename

import FileUtility
from LoadUtility import LoadUtility

class EnterLoad(LoadUtility):

    def __init__(self, callback):
        LoadUtility.__init__(self, callback)
        phasesToScan = ["phase_3.5/models", "phase_4/models"]
        self.models = FileUtility.findAllModelFilesInVFS(phasesToScan)

    def load(self):
        loader.beginBulkLoad('localAvatarEnterGame', 'localAvatarEnterGame', len(self.models), 0, False)
        LoadUtility.load(self)

    def done(self):
        LoadUtility.done(self)
        loader.endBulkLoad('localAvatarEnterGame')

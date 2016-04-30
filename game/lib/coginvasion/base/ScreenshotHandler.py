########################################
# Filename: ScreenshotHandler.py
# Created by: DecodedLogic (19Apr16)
########################################
# System used to combat problems that occur when taking
# screenshots in the same thread as everything else is running in.

from datetime import datetime
from panda3d.core import Filename
import threading

FILEPATH = 'screenshots/'

def __saveScreenshot(shot):
    now = datetime.now().strftime(FILEPATH + 'screenshot-%a-%b-%d-%Y-%I-%M-%S-%f')
    shot.write(Filename(now + '.jpeg'))
    return

def __takeScreenshot():
    shot = base.win.getScreenshot()
    thread = threading.Thread(target = __saveScreenshot, args = (shot,))
    thread.start()
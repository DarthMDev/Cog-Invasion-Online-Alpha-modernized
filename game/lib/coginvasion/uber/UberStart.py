"""

  Filename: UberStart.py
  Created by: DuckyDuck1553 (03Dec14)

"""

import argparse, os, sys
sys.dont_write_bytecode = True

from panda3d.core import *
from direct.showbase import PythonUtil

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--max-channels', help='The number of channels the server may use.')
parser.add_argument('--stateserver', help="The control channel of this UD's designated State Server.")
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.")
parser.add_argument('--eventlogger-ip', help="The IP address of the Astron Event Logger to log to.")
parser.add_argument('config', nargs='*', default = ['config/config_server.prc'], help = "PRC file(s) to load.")
parser.add_argument('--acc-limit', help='The max number of accounts that can be created on the game.')
parser.add_argument('--acc-limit-per-comp', help='The max number of accounts that can be created on each computer.')
parser.add_argument('--holiday', help='The current holiday that is active on the game by index.')
args = parser.parse_args()
__builtins__.args = args

for prc in args.config:
	loadPrcFile(prc)

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
loadPrcFileData('Command-line', localconfig)

class game:
	name = 'uberDog'
	process = 'server'
__builtins__.game = game

from panda3d.core import *

loadPrcFileData('', 'window-type none')
loadPrcFileData('', 'audio-libarary-name none')

from lib.coginvasion.ai.AIBaseGlobal import *

from lib.coginvasion.uber.CogInvasionUberRepository import CogInvasionUberRepository as CIUR
base.air = CIUR(config.GetInt('air-base-channel', 400000000), config.GetInt('air-stateserver', 10000))
base.air.holiday = int(os.environ.get('HOLIDAY'))
host = args.astron_ip
port = 7033
if ':' in host:
	host, port = args.astron_ip.split(':', 1)
	port = int(port)
base.air.connect(host, port)

# I'm embedding the login server into the uberdog process to reduce CPU usage.
#from lib.server.account.LoginServer import *

try:
	base.run()
except SystemExit:
	raise

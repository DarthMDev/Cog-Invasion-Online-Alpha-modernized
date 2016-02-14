from lib.coginvasion.standalone.StandaloneToon import *
from pandac.PandaModules import *

#loadPrcFile('config/config_client.prc')
#loadPrcFileData('', 'load-display pandadx9')

from lib.coginvasion.dna.DNALoader import *
from lib.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from direct.controls.GravityWalker import GravityWalker
from lib.coginvasion.toon.Toon import Toon
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.SmartCamera import SmartCamera
from direct.showbase.Audio3DManager import Audio3DManager
from direct.gui import DirectGuiGlobals
from direct.interval.IntervalGlobal import *
from lib.coginvasion.cog.Suit import Suit
from lib.coginvasion.cog.SuitPathFinderAI import SuitPathFinderAI
from direct.gui.DirectGui import *
from panda3d.core import *
#base.setSleep(0.04)
#from lib.toontown.base.ShadowCreator import ShadowCreator

#caster = ShadowCreator()

#from rp.Code.RenderingPipeline import RenderingPipeline

#render.setAntialias(AntialiasAttrib.MMultisample)

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
"""
ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT_sz.pdna")
node = loadDNAFile(ds, "phase_4/dna/new_ttc_sz.pdna")

if node.getNumParents() == 1:
	geom = NodePath(node.getParent(0))
	geom.reparentTo(hidden)
else:
	geom = hidden.attachNewNode(node)
gsg = base.win.getGsg()
if gsg:
	geom.prepareScene(gsg)
geom.setName('toontown_central')
geom.reparentTo(render)
geom.find('**/toontown_central_beta_DNARoot').setTwoSided(1)
geom.find('**/ground_center').setBin('ground', 18)
geom.find('**/ground_sidewalk').setBin('ground', 18)
geom.find('**/ground').setBin('ground', 18)
geom.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
geom.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)
for face in geom.findAllMatches('**/ground_sidewalk_front_*'):
	face.setColorScale(0.8, 0.8, 0.8, 1.0)
for tunnel in geom.findAllMatches('**/linktunnel_tt*'):
	tunnel.find('**/tunnel_floor_1').setTexture(loader.loadTexture('phase_4/models/neighborhoods/tex/sidewalkbrown.jpg'), 1)
for tree in geom.findAllMatches('**/prop_green_tree_*_DNARoot'):
	newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
	newShadow.reparentTo(tree)
	newShadow.setScale(1.5)
	newShadow.setColor(0, 0, 0, 0.5, 1)
sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
sky.reparentTo(render)
sky.setScale(5)
sky.find('**/cloud1').setSz(0.65)
sky.find('**/cloud2').removeNode()


mdl = loader.loadModel('cog-bldg-modles/cog_bldg_executive_flr.egg')
mdl.reparentTo(render)
mdl.find('**/floor').setBin('ground', 18)

sky = loader.loadModel('phase_3.5/models/props/BR_sky.bam')
sky.reparentTo(render)
sky.setZ(-100)

painting = loader.loadModel('cog-bldg-modles/photo_frame.egg')
painting.reparentTo(render)
painting.setPosHpr(16.26, 63.84, 8.34, 270.0, 0, 90.0)

bookshelf1 = loader.loadModel('phase_11/models/lawbotHQ/LB_bookshelfA.bam')
bookshelf1.reparentTo(render)
bookshelf1.setScale(1.5)
bookshelf1.setPosHpr(-22.11, 49.88, 0.01, 90.0, 0, 0)

bookshelf2 = loader.loadModel('phase_11/models/lawbotHQ/LB_bookshelfB.bam')
bookshelf2.reparentTo(render)
bookshelf2.setScale(1.5)
bookshelf2.setPosHpr(-22.11, 35, 0.01, 90, 0, 0)

plant = loader.loadModel('phase_11/models/lawbotHQ/LB_pottedplantA.bam')
plant.setScale(12)
plant.reparentTo(render)
plant.setPos(20.51, -5.13, 0)

rug1 = loader.loadModel('phase_3.5/models/modules/rug.bam')
rug1.reparentTo(render)

rug2 = loader.loadModel('phase_3.5/models/modules/rug.bam')
rug2.reparentTo(render)
rug2.setPos(0, 52, 0)

clock = loader.loadModel('cog-bldg-modles/clock.egg')
clock.reparentTo(render)
clock.setPosHpr(23.68, 20.95, 9.67, 0, 0, 90)

recepC = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
recepC.reparentTo(render)
recepC.setPosHpr(20.7, 8.14, 0, 270, 0, 0)

recepM = loader.loadModel('cog-bldg-modles/computer_monitor.egg')
recepM.reparentTo(render)
recepM.setPosHpr(13.73, 8.17, 3.99, 270, 0, 0)

recepCC = loader.loadModel('cog-bldg-modles/coffee_cup.egg')
recepCC.reparentTo(render)
recepCC.setPosHpr(14.25, 10.65, 3.99, 78.69, 0, 0)

phone = loader.loadModel('phase_3.5/models/props/phone.bam')
receiver = loader.loadModel('phase_3.5/models/props/receiver.bam')
receiver.reparentTo(phone)
phone.reparentTo(render)
phone.setScale(1.2)
phone.setPosHpr(14.20, 5.29, 3.99, 95.96, 0, 0)

paper1 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper1.reparentTo(render)
paper1.setPosHpr(14.54, 13.34, 4.01, 63.43, 0, 0)

paper2 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper2.reparentTo(render)
paper2.setPosHpr(14.43, 0.72, 4.01, 270, 0, 0)

paper3 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
paper3.reparentTo(render)
paper3.setPosHpr(16.8, 1.14, 4.01, 118.61, 0, 0)

table = loader.loadModel('cog-bldg-modles/meeting_table.egg')
table.reparentTo(render)
table.setPos(-12.7, 5.94, 0)

tableC1 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC1.reparentTo(render)
tableC1.setPosHpr(-22.02, 1.57, 0, 90.0, 0, 0)

tableC2 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC2.reparentTo(render)
tableC2.setPosHpr(-22.02, 10.23, 0, 90.0, 0, 0)

tableC3 = loader.loadModel('phase_11/models/lawbotHQ/LB_chairA.bam')
tableC3.reparentTo(render)
tableC3.setPosHpr(-13.13, 19.73, 0, 0, 0, 0)

tableS = loader.loadModel('phase_3/models/props/square_drop_shadow.bam')
tableS.reparentTo(render)
tableS.setPos(-12.7, 5.94, 0.01)
tableS.setScale(2, 3.5, 1)

elev2 = loader.loadModel('phase_4/models/modules/elevator.bam')
elev2.reparentTo(render)
elev2.setPos(0.23007, 60.47556, 0)

elev1 = loader.loadModel('phase_4/models/modules/elevator.bam')
elev1.reparentTo(render)
elev1.setPos(0.74202, -9.50081, 0)
elev1.setH(180)
elev1.ls()

tableP1 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP1.reparentTo(render)
tableP1.setPosHpr(-16.71, 1.57, 3.4, 270, 0, 0)

tableP2 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP2.reparentTo(render)
tableP2.setPosHpr(-16.71, 10.23, 3.4, 270, 0, 0)

tableP3 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP3.reparentTo(render)
tableP3.setPosHpr(-13.44, 14.8, 3.41, 180, 0, 0)

tableP4 = loader.loadModel('cog-bldg-modles/fax_paper.egg')
tableP4.reparentTo(render)
tableP4.setPosHpr(-13.44, 14.8, 3.4, 150, 0, 0)

base.disableMouse()

#base.localAvatar.enableAvatarControls()
#base.localAvatar.startTrackAnimToSpeed()
#base.localAvatar.attachCamera()
#base.localAvatar.startSmartCamera()
base.localAvatar.reparentTo(hidden)

def printPosHpr():
	print 'Pos: {0}'.format(base.localAvatar.getPos())
	print 'Hpr: {0}'.format(base.localAvatar.getHpr())

base.accept('p', printPosHpr)
"""
tex = loader.loadTexture("bg.tif")
#tex.setMinfilter(Texture.FTNearest)
#tex.setMagfilter(Texture.FTNearest)

base.localAvatar.reparentTo(hidden)

bg = OnscreenImage(image = tex, parent = render2d)

base.cam.node().getDisplayRegion(0).setSort(20)

from lib.coginvasion.cog import SuitBank
from lib.coginvasion.cog import Variant
from lib.coginvasion.cog.DistributedSuit import DistributedSuit

#camera.setH(90)
#camera.setZ(5)
#camera.setY(20)
"""
refNode = NodePath('refNode')
refNode.reparentTo(render)
refNode.setPosHpr(-4.88, 14.68, -6.91, 240.42, 7.77, 353.29)

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit(SuitBank.MrHollywood)
suit.setName("")
suit.reparentTo(refNode)
suit.stopSmooth()
suit.show()
suit.cleanupPropeller()
suit.removeHealthBar()
suit.pose('magic1', 15)

from lib.coginvasion.npc import NPCGlobals

refNodeT = NodePath('ref2Node')
refNodeT.reparentTo(render)

toon = Toon(base.cr)
toon.parseDNAStrand(NPCGlobals.NPC_DNA['Flippy'])
toon.generateToon()
toon.deleteShadow()
toon.setName("")
toon.reparentTo(refNodeT)
pie = loader.loadModel('phase_3.5/models/props/tart.bam')
pie.reparentTo(toon.find('**/joint_Rhold'))
toon.pose('pie', 45)
refNodeT.setPosHpr(3.22, 9, -3.56, 104.04, 9.73, 9.16)
pupilL = toon.controlJoint(None, 'head', 'joint_pupilL')
pupilL.setPosHpr(0.02, 0.08, -3.95, 15.01, 0, 0)
pupilR = toon.controlJoint(None, 'head', 'joint_pupilR')
pupilR.setPosHpr(0.03, 0.07, -3.96, 344.99, 0, 0)
angryEyes = loader.loadTexture('phase_3/maps/eyesAngry.jpg', 'phase_3/maps/eyesAngry_a.rgb')
toon.find('**/eyes').setTexture(angryEyes, 1)
#refNodeT.place()
"""

ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT.pdna")
loadDNAFile(ds, "phase_4/dna/storage_TT_sz.pdna")
node = loadDNAFile(ds, "phase_4/dna/toontown_central_sz.pdna")

if node.getNumParents() == 1:
	geom = NodePath(node.getParent(0))
	geom.reparentTo(hidden)
else:
	geom = hidden.attachNewNode(node)
gsg = base.win.getGsg()
if gsg:
	geom.prepareScene(gsg)
geom.setName('toontown_central')
geom.reparentTo(render)

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit(SuitBank.MrHollywood)
suit.setName("")
suit.reparentTo(render)
suit.stopSmooth()
suit.show()
suit.cleanupPropeller()
suit.removeHealthBar()

from lib.coginvasion.cog.SuitPathDataAI import *

from lib.coginvasion.cog import SuitPathFinder

from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
import time
startTime = time.time()
path = pathfinder.planPath((-30.0, 27.0), (-50, -20))
print time.time() - startTime
#linesegs = LineSegs('visual')
#linesegs.setColor(0, 0, 0, 1)

#for vertex in pathfinder.vertices:
#	#linesegs.drawTo(vertex.prevPolyNeighbor.pos.getX(), vertex.prevPolyNeighbor.pos.getY(), 20)
#	linesegs.drawTo(vertex.nextPolyNeighbor.pos.getX(), vertex.nextPolyNeighbor.pos.getY(), 20)
#node = linesegs.create(False)
#np = render.attachNewNode(node)
"""
from panda3d.core import LineSegs

linesegs = LineSegs('visual')
linesegs.setColor(0, 0, 0, 1)

for point in path:
	linesegs.drawTo(point.getX(), point.getY(), 0)

node = linesegs.create(False)
np = render.attachNewNode(node)
"""
def doPath():
	global path
	if not len(path):
		suit.loop('neutral')
		return
	endX, endY = path[0]
	endPoint = Point3(endX, endY, 0)
	startPoint = suit.getPos(render)
	path.remove(path[0])
	ival = NPCWalkInterval(suit, endPoint, 0.2, startPoint)
	ival.setDoneEvent(suit.uniqueName('guardWalkDone'))
	base.acceptOnce(suit.uniqueName('guardWalkDone'), doPath)
	ival.start()
	suit.loop('walk')


smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
smiley.place()

def makePathandgo():
	point = (smiley.getX(), smiley.getY())
	startPoint = (suit.getX(), suit.getY())
	global path
	path = pathfinder.planPath(startPoint, point)
	if len(path) > 1:
		path.remove(path[0])
	print path
	doPath()

base.accept('p', makePathandgo)

from datetime import datetime

"""
startTime = time.time()



base.setFrameRateMeter(True)











def findPath(task):
	for i in range(101):
		SuitPathFinder.find_path(CIGlobals.DonaldsDreamland, '1', '36')
	print task.time
	return task.again


def start():
	taskMgr.add(findPath, 'findPath')
	
def pause():
	taskMgr.remove('findPath')

base.accept('s', start)
base.accept('p', pause)
print 'start'
print time.time() - startTime
#print datetime.now() - startTime
"""

#render.setAntialias(AntialiasAttrib.MMultisample)

#base.disableMouse()

#refNode.place()

#base.startDirect()

#toon = loader.loadModel('models/smiley')
#toon.reparentTo(elevator1)
#toon.place()

#music = base.loadMusic("phase_7/audio/bgm/encntr_general_bg_indoor.mid")
#base.playMusic(music, volume = 0.25, looping = 1, interrupt = 1)

#spin = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.mp3')
#deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.mp3')

#track = Sequence(Wait(0.8), SoundInterval(spin, duration = 1.2, startTime = 1.5, volume = 0.2), SoundInterval(spin, duration = 3.0, startTime = 0.6, volume = 0.9), SoundInterval(deathSound, volume = 0.4))
#track.start()

#sound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_Full.mp3')
#base.playSfx(sound, volume = 10)

for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(10)
			except:
				pass
	except:
		continue

base.oobe()
base.run()

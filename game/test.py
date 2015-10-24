from pandac.PandaModules import *

loadPrcFile('config/config_client.prc')
import __builtin__
class game:
	process = 'client'
__builtin__.game = game

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from lib.coginvasion.dna.DNAParser import *
from lib.coginvasion.globals import CIGlobals
from direct.controls import ControlManager
from direct.controls.GravityWalker import GravityWalker
from lib.coginvasion.toon.Toon import Toon
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.SmartCamera import SmartCamera
from direct.showbase.Audio3DManager import Audio3DManager
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
#from lib.toontown.base.ShadowCreator import ShadowCreator

#caster = ShadowCreator()

#from rp.Code.RenderingPipeline import RenderingPipeline

render.setAntialias(AntialiasAttrib.MMultisample)

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.dna")
loadDNAFile(ds, "phase_4/dna/storage_TT.dna")
loadDNAFile(ds, "phase_4/dna/storage_TT_sz.dna")
loadDNAFile(ds, "phase_5/dna/storage_town.dna")
loadDNAFile(ds, "phase_5/dna/storage_TT_town.dna")
loadDNAFile(ds, "phase_4/dna/storage_new_TT.dna")
node = loadDNAFile(ds, "phase_4/dna/new_ttc_sz.dna")

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
geom.find('**/toontown_central_DNARoot').setTwoSided(1)
geom.find('**/ground_center').setBin('ground', 18)
geom.find('**/ground_sidewalk').setBin('ground', 18)
geom.find('**/ground').setBin('ground', 18)
#geom.find('**/ground_sidewalk').setH(347.11)
#geom.find('**/ground_sidewalk_coll').setH(347.11)
for tree in geom.findAllMatches('**/prop_green_tree_large*_DNARoot'):
	tree.setBillboardAxis()
	try:
		tree.find('**/prop_green_tree_large_ur_shadow').removeNode()
		treeType = 'ur'
	except:
		tree.find('**/prop_green_tree_large_ul_shadow').removeNode()
		treeType = 'ul'
	newShadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
	newShadow.reparentTo(tree)
	if treeType == 'ur':
		newShadow.setX(1)
	else:
		newShadow.setX(-1)
	newShadow.setScale(1.5)
	newShadow.setColor(0, 0, 0, 0.5, 1)
sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
sky.reparentTo(render)
sky.setScale(5)
sky.find('**/cloud1').setSz(0.65)
sky.find('**/cloud2').removeNode()


music = base.loadMusic("phase_4/audio/bgm/TC_nbrhood.mid")
base.playMusic(music, volume = 0.25, looping = 1, interrupt = 1)

for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(10)
			except:
				pass
	except:
		continue


base.cTrav = CollisionTraverser()
cr = ClientRepository(['astron/direct.dc'])
cr.isShowingPlayerIds = False

def taskName(string):
	return string

controlManager = ControlManager.ControlManager(True, False)
localAv = Toon(cr)
localAv.taskName = taskName
localAv.setDNAStrand("00/01/07/00/00/00/00/00/00/00/00/00/00/00/00")
localAv.setName("Sneaky Toon")
localAv.initCollisions()
localAv.startBlink()
localAv.startLookAround()
localAv.reparentTo(render)
localAv.animFSM.request("neutral")
base.localAvatar = localAv
avatarMoving = False
base.disableMouse()

animal = localAv.getAnimal()
bodyScale = CIGlobals.toonBodyScales[animal]
headScale = CIGlobals.toonHeadScales[animal][2]
shoulderHeight = CIGlobals.legHeightDict[localAv.legs] * bodyScale + CIGlobals.torsoHeightDict[localAv.torso] * bodyScale
height = shoulderHeight + CIGlobals.headHeightDict[localAv.head] * headScale
localAv.setHeight(height)
camHeight = max(localAv.getHeight(), 3.0)
heightScaleFactor = camHeight * 0.3333333333
defLookAt = Point3(0.0, 1.5, camHeight)
camPos = (Point3(0.0, -9.0 * heightScaleFactor, camHeight),
	defLookAt,
	Point3(0.0, camHeight, camHeight * 4.0),
	Point3(0.0, camHeight, camHeight * -1.0),
	0)
"""
av = Toon(cr)
av.setDNAStrand("00/00/00/00/00/00/00/00/00/00/00/00/00/00/00")
av.setName("Tom")
av.initCollisions()
av.startBlink()
av.startLookAround()
av.reparentTo(render)
av.animFSM.request("neutral")
av.setX(-20)

av2 = Toon(cr)
av2.setDNAStrand("00/04/01/00/02/00/01/00/00/00/00/00/00/00/00")
av2.setName("Flippy")
av2.initCollisions()
av2.startBlink()
av2.startLookAround()
av2.reparentTo(render)
av2.animFSM.request("neutral")
av2.setX(-23)
av2.setY(5)
av2.setH(77)
"""

ToonStandableGround = 0.707
ToonSpeedFactor = 1.25
ToonForwardSpeed = 16.0 * ToonSpeedFactor
ToonJumpForce = 24.0
ToonReverseSpeed = 8.0 * ToonSpeedFactor
ToonRotateSpeed = 80.0 * ToonSpeedFactor
ToonForwardSlowSpeed = 6.0
ToonJumpSlowForce = 4.0
ToonReverseSlowSpeed = 2.5
ToonRotateSlowSpeed = 33.0

Y_FACTOR = -0.15

smart_cam = SmartCamera()
smart_cam.initializeSmartCamera()
smart_cam.setIdealCameraPos(camPos[0])
smart_cam.setLookAtPoint(defLookAt)
camera.reparentTo(localAv)
camera.setPos(smart_cam.getIdealCameraPos())
smart_cam.startUpdateSmartCamera()

walkControls = GravityWalker(legacyLifter=False)
walkControls.setWallBitMask(CIGlobals.WallBitmask)
walkControls.setFloorBitMask(CIGlobals.FloorBitmask)
walkControls.setWalkSpeed(ToonForwardSpeed, ToonJumpForce, ToonReverseSpeed, ToonRotateSpeed)
walkControls.initializeCollisions(base.cTrav, localAv, avatarRadius=1.4, floorOffset=0.025, reach=4.0)
walkControls.enableAvatarControls()

def crouch():
	walkControls.setWalkSpeed(ToonForwardSpeed, ToonJumpForce, ToonReverseSpeed, ToonRotateSpeed)
	
def uncrouch():
	walkControls.setWalkSpeed(ToonForwardSpeed, ToonJumpForce, ToonReverseSpeed, ToonRotateSpeed)
	
def moving():
	localAv.animFSM.request('run')
	global avatarMoving
	avatarMoving = True
	
def unmoving():
	localAv.animFSM.request('neutral')
	global avatarMoving
	avatarMoving = False

base.accept("control", crouch)
base.accept("control-up", uncrouch)
base.accept("arrow_up", moving)
base.accept("arrow_up-up", unmoving)
"""

amb = AmbientLight('amblight')
amb.setColor(VBase4(0.5, 0.5, 0.5, 1))
ambNp = render.attachNewNode(amb)
render.setLight(ambNp)

spot = Spotlight('slight')
spot.setColor(VBase4(1, 1, 1, 1))
spot.setShadowCaster(True, 2000, 2000)
spot.setExponent(64)
spotNp = render.attachNewNode(spot)
spotNp.setPos(-30, 5, 100)
spotNp.lookAt(0, 0, 0)
#render.setLight(spotNp)

direc = PointLight('dlight')
direc.setColor(VBase4(1, 1, 1, 1))
direcNp = render.attachNewNode(direc)
direcNp.setZ(5)
direcNp.setY(15)
render.setLight(direcNp)

render.setTwoSided(False)
render.setShaderAuto()
"""


# Used for rotating buildings in the outer circle around.
#bldgNode = NodePath()
#bldgNode.attachNewNode(geom.find('**/sz0:random_DNARoot'))
#bldgNode.attachNewNode(geom.find('**/sz0:random_2_DNARoot'))
#bldgNode.attachNewNode(geom.find('**/linktunnel_tt_2132_DNARoot'))
#bldgNode.attachNewNode(geom.find('**/sz18:toon_landmark_TT_library_DNARoot'))
#bldgNode.attachNewNode(geom.find('**/

#geom.find('**/buildings').place()

#geom.find('**/prop_green_tree_large_ur_2_DNARoot').place()

#caster.shadowCamera.place()


#base.oobe()
#base.startDirect()
base.run()

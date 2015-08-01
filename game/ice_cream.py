from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'tk-main-loop 0')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.controls.ControlManager import CollisionHandlerRayStart
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.dna.DNAParser import *
import __builtin__
class game:
	process = 'client'
__builtin__.game = game
from lib.coginvasion.hood.DistributedGagShop import DistributedGagShop
from lib.coginvasion.suit.CogStation import CogStation
from direct.distributed.ClientRepository import ClientRepository
from Tkinter import *
base.startTk()

base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()

ds = DNAStorage()

loadDNAFile(ds, "phase_4/dna/storage.dna")
loadDNAFile(ds, "phase_8/dna/storage_DL.dna")
loadDNAFile(ds, "phase_8/dna/storage_DL_sz.dna")
node = loadDNAFile(ds, "phase_8/dna/donalds_dreamland_sz.dna")

if node.getNumParents() == 1:
	geom = NodePath(node.getParent(0))
	geom.reparentTo(hidden)
else:
	geom = hidden.attachNewNode(node)
gsg = base.win.getGsg()
if gsg:
	geom.prepareScene(gsg)
geom.reparentTo(render)

partyGate = geom.find('**/prop_party_gate_DNARoot')
if not partyGate.isEmpty():
	partyGate.removeNode()
del partyGate


"""
base.setBackgroundColor(0.05, 0.05, 0.05)
fog = Fog("DEagleGame-sceneFog")
fog.setColor(0.05, 0.05, 0.05)
fog.setExpDensity(0.01)
render.setFog(fog)
turret = loader.loadModel("phase_4/models/minigames/toon_cannon.bam")
turret.reparentTo(render)
"""

class Points:

	def __init__(self):
		self.points = []
		self.lastPoint = None

	def createPoint(self):
		tn = TextNode('tn')
		tn.setText("Point " + str(len(self.points) + 1))
		tn.setAlign(TextNode.ACenter)
		tnp = render.attachNewNode(tn)
		tnp.reparentTo(render)
		if self.lastPoint:
			tnp.setPos(self.lastPoint.getPos(render))
		cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
		cRayNode = CollisionNode('pointray')
		cRayNode.addSolid(cRay)
		cRayNodePath = tnp.attachNewNode(cRayNode)
		cRayBitMask = CIGlobals.FloorBitmask
		cRayNode.setFromCollideMask(cRayBitMask)
		cRayNode.setIntoCollideMask(BitMask32.allOff())
		lifter = CollisionHandlerFloor()
		lifter.addCollider(cRayNodePath, tnp)
		base.cTrav.addCollider(cRayNodePath, lifter)

		cSphere = CollisionSphere(0.0, 0.0, 1, 0.01)
		cSphereNode = CollisionNode('pointfc')
		cSphereNode.addSolid(cSphere)
		cSphereNodePath = tnp.attachNewNode(cSphereNode)

		cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
		cSphereNode.setIntoCollideMask(BitMask32.allOff())

		pusher = CollisionHandlerPusher()
		pusher.addCollider(cSphereNodePath, tnp)
		floorCollNodePath = cSphereNodePath
		base.cTrav.addCollider(cSphereNodePath, pusher)
		#if self.lastPoint:
		#   self.lastPoint.place()
		self.lastPoint = tnp

	def placeLastPoint(self):
		self.lastPoint.place()

class IceCreamPoints(Points):

	def __init__(self):
		Points.__init__(self)
		#for key in CIGlobals.SuitSpawnPoints[CIGlobals.TheBrrrgh].keys():
		#	self.createPoint()
		#	self.lastPoint.setPos(CIGlobals.SuitSpawnPoints[CIGlobals.TheBrrrgh][key])
		#	self.lastPoint.node().setText("Spawn Point " + key)

	def createPoint(self):
		Points.createPoint(self)
		self.lastPoint.node().setText("Spawn Point " + str(len(self.points) + 1))
		self.lastPoint.node().setTextColor(1, 1, 1, 1)
		self.lastPoint.setBillboardAxis()
		self.points.append(self.lastPoint)

#health = IceCreamPoints()

#def createICPoint():
#	health.createPoint()
#	health.placeLastPoint()

#newWalkBtn = Button(base.tkRoot, text = "Spawn Point", command = createICPoint)
#newWalkBtn.pack()

station = CogStation()
station.generateStation()
station.reparentTo(render)
station.place()

base.oobe()
base.run()

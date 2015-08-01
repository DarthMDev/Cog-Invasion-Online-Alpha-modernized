from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 16')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.controls.ControlManager import CollisionHandlerRayStart
from Tkinter import *
from direct.gui.OnscreenText import OnscreenText
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.Suit import Suit
from direct.distributed.ClientRepository import ClientRepository
from collections import deque
from lib.coginvasion.dna.DNAParser import *
#base.startTk()
import random

base.cTrav = CollisionTraverser()
base.cr = ClientRepository([])
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
		cRayBitMask = ToontownGlobals.FloorBitmask
		cRayNode.setFromCollideMask(cRayBitMask)
		cRayNode.setIntoCollideMask(BitMask32.allOff())
		lifter = CollisionHandlerFloor()
		lifter.addCollider(cRayNodePath, tnp)
		base.cTrav.addCollider(cRayNodePath, lifter)

		cSphere = CollisionSphere(0.0, 0.0, 1, 0.01)
		cSphereNode = CollisionNode('pointfc')
		cSphereNode.addSolid(cSphere)
		cSphereNodePath = tnp.attachNewNode(cSphereNode)

		cSphereNode.setFromCollideMask(ToontownGlobals.FloorBitmask)
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

class WalkPoints(Points):

	def __init__(self):
		Points.__init__(self)

	def createPoint(self):
		Points.createPoint(self)
		self.lastPoint.node().setText("Walk Point " + str(len(self.points) + 1))
		self.lastPoint.setBillboardAxis()
		self.points.append(self.lastPoint)

class GuardPoints(Points):

	def __init__(self):
		Points.__init__(self)

	def createPoint(self):
		Points.createPoint(self)
		self.lastPoint.node().setText("Guard Point " + str(len(self.points) + 1))
		self.lastPoint.node().setTextColor(VBase4(0.5, 0.5, 1, 1.0))
		self.lastPoint.setTwoSided(1)
		self.points.append(self.lastPoint)
"""
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

partyGate = geom.find('**/prop_party_gate_DNARoot')
if not partyGate.isEmpty():
	partyGate.removeNode()
del partyGate

geom.reparentTo(render)
"""
walks = WalkPoints()
guards = GuardPoints()

def writeWPoint():
	pointfile = open("factory_sneak_guard_walk_points.py", "a")
	pointfile.write("\n" + str(walks.lastPoint.getX()) + " " + str(walks.lastPoint.getY()) + " " + str(walks.lastPoint.getZ()))
	pointfile.flush()
	pointfile.close()
	del pointfile

def createWPoint():
	walks.createPoint()
	walks.placeLastPoint()

def writeGPoint():
	pointfile = open("factory_sneak_guard_guard_points.py", "a")
	pointfile.write("\n" + str(guards.lastPoint.getX()) + " " + str(guards.lastPoint.getY()) + " " + str(guards.lastPoint.getZ()) + "|" + str(guards.lastPoint.getH()) + " " + str(guards.lastPoint.getP()) + " " + str(guards.lastPoint.getR()))
	pointfile.flush()
	pointfile.close()
	del pointfile

def createGPoint():
	guards.createPoint()
	guards.placeLastPoint()

newWalkBtn = Button(base.tkRoot, text = "Walk Point", command = createWPoint)
newWalkBtn.pack()
walkPointDoneBtn = Button(base.tkRoot, text = "WP Done", command = writeWPoint)
walkPointDoneBtn.pack()
newGuardBtn = Button(base.tkRoot, text = "Guard Point", command = createGPoint)
newGuardBtn.pack()
gPointDoneBtn = Button(base.tkRoot, text = "GP Done", command = writeGPoint)
gPointDoneBtn.pack()

pointfile = open("factory_sneak_guard_walk_points.py", "r")
for line in pointfile.readlines():
	x, y, z = line.split(' ')
	x = float(x)
	y = float(y)
	z = float(z)
	walks.createPoint()
	walks.lastPoint.setPos(Point3(x, y, z))
pointfile.close()
del pointfile

pointfile = open("factory_sneak_guard_guard_points.py", "r")
for line in pointfile.readlines():
	pos, hpr = line.split('|')
	x, y, z = pos.split(' ')
	h, p, r = hpr.split(' ')
	x = float(x)
	y = float(y)
	z = float(z)
	h = float(h)
	p = float(p)
	r = float(r)
	guards.createPoint()
	guards.lastPoint.setPos(Point3(x, y, z))
	guards.lastPoint.setHpr(Vec3(h, p, r))
pointfile.close()
del pointfile
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.interval.IntervalGlobal import *

base.disableMouse()

node = NodePath('baseNode')
node.reparentTo(render)

collisionSphere = CollisionSphere(0, 0, 0, 2)
sensorNode = CollisionNode("sensors")
sensorNode.addSolid(collisionSphere)
sensorNodePath = node.attachNewNode(sensorNode)
sensorNodePath.setZ(2.5)
sensorNodePath.setSz(2)
sensorNodePath.setCollideMask(BitMask32(0))
sensorNodePath.node().setFromCollideMask(CIGlobals.WallBitmask)
sensorNodePath.show()
event = CollisionHandlerEvent()
event.setInPattern("%fn-into")
event.setOutPattern("%fn-out")
base.cTrav.addCollider(sensorNodePath, event)

cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
cRayNode = CollisionNode('ray' + 'r')
cRayNode.addSolid(cRay)
cRayNodePath = node.attachNewNode(cRayNode)
cRayBitMask = CIGlobals.FloorBitmask
cRayNode.setFromCollideMask(cRayBitMask)
cRayNode.setIntoCollideMask(BitMask32.allOff())
lifter = CollisionHandlerFloor()
lifter.addCollider(cRayNodePath, node)
base.cTrav.addCollider(cRayNodePath, lifter)

cSphere = CollisionSphere(0.0, 0.0, 2, 0.01)
cSphereNode = CollisionNode('sphere' + 'fc')
cSphereNode.addSolid(cSphere)
cSphereNodePath = node.attachNewNode(cSphereNode)

cSphereNode.setFromCollideMask(CIGlobals.FloorBitmask)
cSphereNode.setIntoCollideMask(BitMask32.allOff())

pusher = CollisionHandlerPusher()
pusher.addCollider(cSphereNodePath, node)
floorCollNodePath = cSphereNodePath
base.cTrav.addCollider(cSphereNodePath, pusher)

#base.disableMouse()

camera.reparentTo(node)
camera.setY(-10)
camera.setZ(2)

#snowsphere = CollisionSphere(0.0, 0.0, 0.0, 25)
#snownode = CollisionNode('DistributedPieTurret.WallSphere')
#snownode.addSolid(snowsphere)
#snownode.setCollideMask(CIGlobals.WallBitmask)
#wallCollNode = geom.attachNewNode(snownode)
#wallCollNode.show()
#wallCollNode.setPos(-109.00, -39.86, 0.00)

class WayPointTest:

	def __init__(self, point, number):
		self.point = point
		self.number = number
		self.wayPointsToTest = dict(CIGlobals.SuitSpawnPoints[CIGlobals.DonaldsDreamland])
		del self.wayPointsToTest[number]
		self.finalList = []
		self.currentWayPointTestKey = None
		self.numberOfTests = -1
		self.movementIval = None
		self.allTestsDone = False
		print "Testing waypoint: " + str(number)
		self.testNextWayPoint()

	def allTestsCompleted(self):
		print "Done testing waypoint: " + str(self.number)
		self.allTestsDone = True

	def testNextWayPoint(self):
		self.numberOfTests += 1
		if self.movementIval:
			self.movementIval.pause()
			self.movementIval = None
		if self.numberOfTests > len(self.wayPointsToTest.keys()) - 1:
			self.allTestsCompleted()
			return
		print "Test number " + str(self.numberOfTests) + " on waypoint " + str(self.number)
		self.currentWayPointTestKey = self.wayPointsToTest.keys()[self.numberOfTests]
		self.movementIval = NPCWalkInterval(node, self.wayPointsToTest[self.currentWayPointTestKey],
			0.01, startPos = self.point, fluid = 1)
		self.movementIval.setDoneEvent('testWayPointDone')
		base.acceptOnce(self.movementIval.getDoneEvent(), self.currentTestSucceeded)
		base.acceptOnce("sensors-into", self.handleBadTest)
		self.movementIval.start()

	def handleBadTest(self, entry):
		print "Failed"
		base.ignore("sensors-into")
		base.ignore("sensors-out")
		base.ignore(self.movementIval.getDoneEvent())
		self.movementIval.pause()
		self.movementIval = None
		self.testNextWayPoint()

	def currentTestSucceeded(self):
		print "Passed"
		base.ignore("sensors-into")
		base.ignore("sensors-out")
		base.ignore(self.movementIval.getDoneEvent())
		self.finalList.append(self.currentWayPointTestKey)
		self.testNextWayPoint()

class WayPointTests:

	def __init__(self):
		self.finalDict = {}
		self.wayPointsToTest = dict(CIGlobals.SuitSpawnPoints[CIGlobals.DonaldsDreamland])
		self.numberOfTests = -1
		self.currentWayPointTestKey = None
		self.currentTest = None
		print "Starting waypoint tests..."
		self.testNextWayPoint()

	def testNextWayPoint(self):
		self.numberOfTests += 1
		if self.numberOfTests > len(self.wayPointsToTest.keys()) - 1:
			self.done()
			return
		print "Test number: " + str(self.numberOfTests)
		self.currentWayPointTestKey = self.wayPointsToTest.keys()[self.numberOfTests]
		point = self.wayPointsToTest[self.currentWayPointTestKey]
		self.currentTest = WayPointTest(point, self.currentWayPointTestKey)
		taskMgr.add(self.watchTestStatus, "watchCurrentTestStatus")

	def watchTestStatus(self, task):
		if self.currentTest.allTestsDone == True:
			self.finalDict[self.currentWayPointTestKey] = self.currentTest.finalList
			self.currentTest = None
			self.testNextWayPoint()
			return task.done
		return task.cont

	def done(self):
		open("dl_suit_accessible_waypoints.py", "w").write(str(self.finalDict))
		print "Completed!"
		sys.exit()

WayPointTests()
"""

from lib.toontown.minigame import CogGuardGlobals as CGG
from lib.toontown.npc.NPCWalker import *
import random

cog = Suit()
cog.generateSuit("A", "mrhollywood", "s", 132, 0)
cog.setName("Mr. Hollywood", "mrhollywood")
cog.setupNameTag()
cog.animFSM.request('neutral')
cog.reparentTo(render)
guardPoint = random.randrange(1, 31)
print guardPoint
cog.setPos(CGG.FactoryWalkPoints['52'])
"""
"""
def findClosestWayPoint(pos, returnId = False):
	distances = {}
	shortestDistance = 999
	closestPoint = None
	for waypoint in CGG.FactoryWalkPoints:
		id = waypoint
		waypoint = CGG.FactoryWalkPoints[waypoint]
		distance = (pos - waypoint).length()
		distances.update({id : [id, distance]})
	for distance in distances:
		distance = distances[distance]
		if distance[1] < shortestDistance:
			shortestDistance = distance[1]
			closestPoint = distance[0]
	if shortestDistance != 999 and closestPoint:
		print "Closest Waypoint: %s. Shortest distance: %s." % (closestPoint, shortestDistance)
		if not returnId:
			return CGG.FactoryWalkPoints[closestPoint]
		else:
			return [closestPoint, CGG.FactoryWalkPoints[closestPoint]]
	else:
		return None
def findPath(graph, start, end):
	Method to determine if a pair of vertices are connected using BFS

   Args:
	 start, end: vertices for the traversal.

   Returns:
	 [start, v1, v2, ... end]

		doesnt check for distance
	path = []
	q = deque()
	q.append(start)
	while len(q):
	  tmp_vertex = q.popleft()
	  if tmp_vertex not in path:
		path.append(tmp_vertex)

	  if tmp_vertex == end:
		return path

	  for vertex in graph[tmp_vertex]:
		if vertex not in path:
		  q.append(vertex)
	return path

closestWalkPoint = findClosestWayPoint(cog.getPos(render), returnId = True)
destination = CGG.FactoryGuardPoints['1'][0]
farthestWalkPoint = findClosestWayPoint(destination, returnId = True)

path = findPath(CGG.FactoryWayPointData, closestWalkPoint[0], farthestWalkPoint[0])
print path
"""
"""
class CogFactoryWander:

	def __init__(self, cog, currentWayPoint = None, lastWayPoint = None, path = None):
		self.cog = cog
		self.walkIval = None
		self.currentWayPoint = currentWayPoint
		self.lastWayPoint = lastWayPoint
		self.path = path

	def startWandering(self):
		if not self.currentWayPoint:
			self.currentWayPoint = self.path[0]
		else:
			self.lastWayPoint = self.currentWayPoint
			self.currentWayPoint = self.path[self.path.index(self.currentWayPoint) + 1]
		self.walkIval = NPCWalkInterval(self.cog, CGG.FactoryWalkPoints[self.currentWayPoint], 0.1, startPos = self.cog.getPos(render))
		self.walkIval.setDoneEvent('wanderIvalDone')
		self.walkIval.start()
		self.cog.animFSM.request('walk')
		base.acceptOnce(self.walkIval.getDoneEvent(), self.wanderFinished)

	def wanderFinished(self):
		self.cog.animFSM.request('neutral')
		self.wanderAgain()

	def wanderAgain(self):
		if self.walkIval:
			self.walkIval.pause()
			self.walkIval = None
		newWayPoint = self.path[self.path.index(self.currentWayPoint) + 1]
		print "Old way point: " + str(self.currentWayPoint)
		print "New way point: " + newWayPoint
		self.walkIval = NPCWalkInterval(self.cog, CGG.FactoryWalkPoints[newWayPoint], 0.1, startPos = self.cog.getPos(render))
		self.walkIval.setDoneEvent('wanderIvalDone')
		self.walkIval.start()
		self.lastWayPoint = self.currentWayPoint
		self.currentWayPoint = newWayPoint
		self.cog.animFSM.request('walk')
		base.acceptOnce(self.walkIval.getDoneEvent(), self.wanderFinished)
#wander = CogFactoryWander(cog, path = path)
#wander.startWandering()

class CogPathFinder:

	def __init__(self, cog, destination, currentPoint, destinationHpr = None):
		self.cog = cog
		self.destination = destination
		self.currentPoint = currentPoint
		self.destinationHpr = destinationHpr
		self.closestPointToDest = None
		self.walkIval = None
		self.pathsVisited = []
		self.start()

	def recalculate(self):
		self.closestPointToDest = None
		self.walkIval = None
		self.pathsVisited = []
		self.start()

	def start(self):
		print "Calculating route!"
		distanceDict = {}
		for waypointKey in CGG.FactoryWalkPoints.keys():
			waypoint = CGG.FactoryWalkPoints[waypointKey]
			distance = (waypoint - Point3(self.destination)).length()
			distanceDict[waypointKey] = distance
		array = []
		for distance in distanceDict.values():
			array.append(distance)
		array.sort()
		for distanceKey in distanceDict.keys():
			distance = distanceDict[distanceKey]
			if distance == array[0]:
				self.closestPointToDest = distanceKey
		del distanceDict
		del array
		del distanceKey
		del distance
		del waypointKey
		del waypoint
		self.walk()

	def findPath(self):
		accessiblePaths = CGG.FactoryWayPointData[self.currentPoint]
		#dummyNode = NodePath('dummyNode')
		#dummyNode.reparentTo(render)
		distanceDict = {}
		for waypointKey in accessiblePaths:
			waypoint = CGG.FactoryWalkPoints[waypointKey]
			#dummyNode.setPos(render)
			distance = (waypoint - Point3(self.destination)).length()
			distanceDict[waypointKey] = distance
		array = []
		for distance in distanceDict.values():
			array.append(distance)
		array.sort()
		closestPointToDest = None
		for distanceKey in distanceDict.keys():
			distance = distanceDict[distanceKey]
			if not distanceKey in self.pathsVisited:
				if distance == array[0]:
					closestPointToDest = distanceKey
		return [closestPointToDest, distanceDict]

	def isValidPath(self, point):
		accessiblePaths = CGG.FactoryWayPointData[point]
		if (CGG.FactoryWalkPoints[self.currentPoint] - Point3(self.destination)).length() < (CGG.FactoryWalkPoints[point] - Point3(self.destination)) and point not in self.pathsVisited:
			return True
		return False

	def walk(self):
		point, distanceDict = self.findPath()
		#if not self.isValidPath(point):
		#	del distanceDict[point]
		#	point = random.choice(distanceDict.keys())
		self.walkIval = NPCWalkInterval(self.cog, CGG.FactoryWalkPoints[point], 0.04, startPos = self.cog.getPos(render))
		self.walkIval.setDoneEvent('walkDone')
		base.acceptOnce("walkDone", self.handleWalkDone)
		self.walkIval.start()
		self.cog.animFSM.request('walk')
		self.currentPoint = point

	def walkToDestination(self):
		self.walkIval = NPCWalkInterval(self.cog, self.destination, 0.04, startPos = self.cog.getPos(render))
		self.walkIval.setDoneEvent("walkToDestDone")
		base.acceptOnce("walkToDestDone", self.handleWalkToDestDone)
		self.walkIval.start()
		self.cog.animFSM.request('walk')

	def handleWalkToDestDone(self):
		self.cog.animFSM.request('neutral')
		if self.destinationHpr:
			self.cog.setHpr(self.destinationHpr)

	def handleWalkDone(self):
		self.pathsVisited.append(self.currentPoint)
		if self.currentPoint == self.closestPointToDest:
			print "You, have arrived!"
			self.walkToDestination()
		else:
			print "Turn to your next waypoint, in 0 feet."
			self.walk()

path = CogPathFinder(cog, CGG.FactoryGuardPoints['1'][0], '52', CGG.FactoryGuardPoints['1'][1])

base.disableMouse()

def watchCog(task):
	camera.setPos(cog.getPos(render) + (0, -20, 10))
	return task.again

taskMgr.add(watchCog, "watchCog")


#render.setTwoSided(True)
"""

#base.disableMouse()
render.setAntialias(AntialiasAttrib.MMultisample)

base.camLens.setMinFov(70.0 / (4./3.))
#base.oobe()
base.run()

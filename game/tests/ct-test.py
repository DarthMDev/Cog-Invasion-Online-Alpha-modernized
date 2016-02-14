from panda3d.core import *
vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

from Tkinter import *

from direct.directutil import Mopath
from direct.interval.IntervalGlobal import *

from lib.coginvasion.standalone.StandaloneToon import *
from direct.controls.ControlManager import CollisionHandlerRayStart
from lib.coginvasion.globals import CIGlobals
base.camLens.setFar(2000.0)

area = loader.loadModel('new-cog-area/cogtropolis.egg')
area.reparentTo(render)


class NURBSMopath():
    
    def __init__(self, curve, name = None):
        if (name == None):
            name = 'nurbsmopath'
        self.name = name
        self.duration = 1.0
        self.node = None
        self.loop = False
        self.cnpRef = None
        self.rope = None
        self.evaluator = None
        self.nurbs = None
        self.tDisplace = 0
        self.tCurrent = 0
        self.loopNum = 0
        if curve:
            if isinstance(curve, str):
                self.loadCurves(curve)
            elif isinstance(curve, NodePath):
                self.cnpRef = curve
                self.__extractCurves(curve)
            elif isinctance(curve, RopeNode):
                self.setCurve(curve)
        print self.name
        
    def loadCurves(self, fname, parent = render):
        if self.cnpRef:
            self.cnpRef.detachNode()
        self.cnpRef = loader.loadModel(fname, noCache=True)
        #self.cnpRef.reparentTo(parent)
        if self.cnpRef:
            if not self.__extractCurves(self.cnpRef):
                print 'NURBSMopath: can\'t find any curves in file: %s' % fname
        else:
            print 'NURBSMopath: no data in file: %s' % fname
            
    def setCurve(self, curve):
            self.rope = NodePath(curve)
            self.evaluator = curve.getCurve()
            self.nurbs = self.evaluator.evaluate()
            
    def __extractCurves(self, np):
        node = np.node()
        if isinstance(node, RopeNode):
            self.setCurve(node)
            return True
        else:
            for ch in np.getChildren():
               if self.__extractCurves(ch):
                   return True
                   
    def __playTask(self, task):
        start, stop = self.getRange()
        delta = stop - start
        scaled_duration = delta * self.duration
        self.loopNum = int(task.time / scaled_duration)
        if (not self.loop) and (self.loopNum > 0):
            self.finish()
            messenger.send(self.name + '-done')
            self.node = None
            return task.done
        t = self.nurbs.getStartT() + (task.time - \
            (self.loopNum * scaled_duration)) / self.duration + \
            self.tDisplace
        print self.tDisplace
        print t
        self.tCurrent = t
        self.goto(t)
        return task.cont
        
    def getRange(self):
        if self.nurbs:
            return (self.nurbs.getStartT(), self.nurbs.getEndT())
        else:
            return (0, 0)
        
    def goto(self, t):
        if self.node:
            p = Point3()
            v = Vec3()
            self.nurbs.evalPoint(t, p)
            self.node.setPos(self.rope, p)
            self.nurbs.evalTangent(t, v)
            v = render.getRelativeVector(self.rope, v)
            currH = v.getY()
            self.node.lookAt(self.node.getPos() + v)
            if abs(self.lastH - currH) > 0.01:
                for node in ['leftFrontWheel', 'rightFrontWheel']:
                    rim = self.node.find('**/' + node)
                    if node == 'rightFrontWheel':
                        rim.setH(-(self.lastH - currH))
                    else:
                        rim.setH(self.lastH - currH)
            else:
                for node in ['leftFrontWheel', 'rightFrontWheel']:
                    rim = self.node.find('**/' + node)
                    rim.setH(0)
            self.lastH = currH	
        
    def play(self, node, duration = 1.0, resume = False, loop = False, startT = 0.0):
        if self.nurbs:
            if not resume:
                self.lastTime = 0
            self.node = node
            self.duration = duration
            self.loop = loop
            self.stop()
            self.tDisplace = startT
            self.lastH = 0
            t = taskMgr.add(self.__playTask, self.name + '-play')
        else:
            print 'NURBSMopath: has no curve.'
        
    def stop(self):
        self.tDisplace = self.tCurrent
        taskMgr.remove(self.name + '-play')
        
    def finish(self):
        start,stop = self.getRange()
        self.tDisplace = 0
        taskMgr.remove(self.name + '-play')


bldg = None

from lib.coginvasion.cogtropolis import TrafficLight

bldgPoints = [
	Point3(0, 0, 0),
	Point3(0, 95, 0),
	Point3(75, 0, 0),
	Point3(75, 95, 0),
	
	Point3(-110, 0, 0),
	Point3(-185, 0, 0),
	Point3(-110, 95, 0),
	Point3(-185, 95, 0),
	
	Point3(-296.5, 0, 0),
	Point3(-296.5, 95, 0),
	Point3(-372, 95, 0),
	Point3(-372, 0, 0),
	
	Point3(189, 0, 0),
	Point3(189, 95, 0),
	Point3(264, 95, 0),
	Point3(264, 0, 0),
	
	Point3(264, 221.5, 0),
	Point3(264, 318, 0),
	Point3(188, 318, 0),
	Point3(188, 221.5, 0),
	
	Point3(75, 221.5, 0),
	Point3(75, 318, 0),
	Point3(0, 221.5, 0),
	Point3(0, 318, 0),
	
	Point3(-110, 318, 0),
	Point3(-110, 221.5, 0),
	Point3(-185, 318, 0),
	Point3(-185, 221.5, 0),
	
	Point3(-296.5, 318, 0),
	Point3(-296.5, 221.5, 0),
	Point3(-372, 318, 0),
	Point3(-372, 221.5, 0),
]

bldgSectionData = [
	[Point3(0, 0, 0), Vec3(0, 0, 0)],
	[Point3(-38.59, -43.57, 0), Vec3(180, 0, 0)]
]

for i in range(2):
	bldgSectionNode = render.attachNewNode('bldgSection' + str(i))
	bldgSectionNode.setPos(bldgSectionData[i][0])
	bldgSectionNode.setHpr(bldgSectionData[i][1])
	for point in bldgPoints:
		bldg = loader.loadModel('cogtropolis_big_building_1.egg')
		bldg.reparentTo(bldgSectionNode)
		bldg.setPos(point)


def makeBuildingAndPlace():
	global bldg
	oldBldg = bldg
	bldg = loader.loadModel('cogtropolis_big_building_1.egg')
	bldg.reparentTo(render)
	if oldBldg:
		bldg.setPos(oldBldg.getPos(render))
	bldg.place()
	
tlightnode = None

tLightData = [
	[(0.71, -2.06, 0.0), (0, 0, 0)],
	[(0.71, -226.17, -0.59), (0, 0, 0)],
	[(0.71, -451.44, 0.0), (0, 0, 0)],
	[(0.71, 221.32, 0), (0, 0, 0)],
	[(-39.05, 404.94, 0), (180, 0, 0)],
	[(-221.31, 404.94, 0.0), (180, 0, 0)],
	[(147.93, 404.94, 0), (180, 0, 0)],
	[(187.76, 221.68, 0), (0, 0, 0)],
	[(187.76, -1.82, 0), (0, 0, 0)],
	[(187.76, -227.4, -0.59), (0, 0, 0)],
	[(187.76, -451.28, 0), (0, 0, 0)],
	[(-185.21, -451.28, 0), (0, 0, 0)],
	[(-185.21, -226.94, 0), (0, 0, 0)],
	[(-185.21, -1.95, 0), (0, 0, 0)],
	[(-185.21, 221.7, 0), (0, 0, 0)]
]

for data in tLightData:
	node = render.attachNewNode('tlight-intersection-holder')
	node.setPos(data[0])
	node.setHpr(data[1])
	
	light = TrafficLight.TrafficLight()
	light.reparentTo(node)
	light.startFlashing()

	light2 = TrafficLight.TrafficLight(1)
	light2.reparentTo(node)
	light2.startFlashing()
	
def makeTLightAndPlace():
	global tlightnode
	oldTLightNode = tlightnode
	tlightnode = render.attachNewNode('tlight-intersection-holder')
	if oldTLightNode:
		tlightnode.setPos(oldTLightNode.getPos(render))
		tlightnode.setHpr(oldTLightNode.getHpr(render))
	light = TrafficLight.TrafficLight()
	light.reparentTo(tlightnode)
	light.startFlashing()

	light2 = TrafficLight.TrafficLight(1)
	light2.reparentTo(tlightnode)
	light2.startFlashing()
	
	tlightnode.place()
	
connector = None
	
def makeConnectorAndPlace():
	global connector
	oldC = connector
	connector = loader.loadModel('new-cog-area/cogtropolis_streetlight_connector.egg')
	connector.setTwoSided(1)
	if oldC:
		connector.setPos(oldC.getPos(render))
		connector.setHpr(oldC.getHpr(render))
	connector.reparentTo(render)
	connector.place()
	
from lib.coginvasion.cogtropolis.CTSuitData import WALK_POINTS
	
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
		#if self.lastPoint:
		#	tnp.setPos(self.lastPoint.getPos(render))
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

class SpawnPoints(Points):

	def __init__(self):
		Points.__init__(self)

	def createPoint(self):
		Points.createPoint(self)
		self.lastPoint.node().setText("Suit Point " + str(len(self.points) + 1))
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
sPoints = SpawnPoints()

def makeSPoint():
	sPoints.createPoint()
	sPoints.placeLastPoint()
	
value = WALK_POINTS[0]

for sidewalk in area.findAllMatches('**/sidewalk*'):
	if not '_coll' in sidewalk.getName():
		sPoints.createPoint()
		sPoints.lastPoint.reparentTo(sidewalk)
		sPoints.lastPoint.setPos(*value['spawn'])

		for exitPoint in value['exitSpawn']:
			sPoints.createPoint()
			sPoints.lastPoint.reparentTo(sidewalk)
			sPoints.lastPoint.setPos(*exitPoint)

		for cornerPoint in value['corners']:
			sPoints.createPoint()
			sPoints.lastPoint.reparentTo(sidewalk)
			sPoints.lastPoint.setPos(*cornerPoint)
			print sPoints.lastPoint.getPos()
"""
#newWalkBtn = Button(base.tkRoot, text = "Suit Point", command = makeSPoint)
#newWalkBtn.pack()

"""
suitFog = Fog("suitFog")
suitFog.setColor(0.3, 0.3, 0.3)
suitFog.setExpDensity(0.0075)
render.setFog(suitFog)
"""

sky = loader.loadModel('phase_9/models/cogHQ/cog_sky.bam')
sky.setScale(5.0)
#sky.setFogOff()
sky.reparentTo(camera)
ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
sky.node().setEffect(ce)

#from lib.coginvasion.hood.SkyUtil import SkyUtil
#skyUtil = SkyUtil()
#skyUtil.startSky(sky)

from lib.coginvasion.suit.Suit import Suit

#suit = DistributedSuit(base.cr)
#suit.doId = 0
#suit.generate()
#suit.announceGenerate()
#suit.setSuit("A", "mrhollywood", "s", 0)
#suit.reparentTo(render)
#suit.animFSM.request('die')
#suit.setX(10)

base.disableMouse()
base.localAvatar.attachCamera()
base.localAvatar.startSmartCamera()

bgm = base.loadMusic('phase_9/audio/bgm/encntr_suit_HQ_nbrhood.mid')
base.playMusic(bgm, looping = 1)

car = loader.loadModel('phase_12/models/bossbotHQ/Coggolf_cart3.bam')
carnode = render.attachNewNode('carnode')
car.reparentTo(carnode)
car.setH(180)
car.ls()

suitInCar = Suit()
suitInCar.generateSuit("C", "gladhander", "s", 137, 0, False)
suitInCar.loop('sit')
suitInCar.disableRay()
suitInCar.setScale(0.7)
suitInCar.setH(180)
suitInCar.setZ(-1.5)
suitInCar.setY(-1)
suitInCar.reparentTo(car.find('**/seat1'))

#camera.reparentTo(car)
#camera.setZ(5)
#camera.setY(20)
#camera.setH(180)

soundDriveByHonk = base.audio3d.loadSfx('new-cog-area/cogtropolis_citycar_driveby_horn.mp3')
base.audio3d.attachSoundToObject(soundDriveByHonk, car)
soundCarRun = base.audio3d.loadSfx('phase_6/audio/sfx/KART_Engine_loop_0.wav')
base.audio3d.attachSoundToObject(soundCarRun, car)
soundDriveBy = base.audio3d.loadSfx('new-cog-area/cogtropolis_citycar_driveby.mp3')
base.audio3d.attachSoundToObject(soundDriveBy, car)

import random

spinSpeed = 3000

def __carDrive(task):
	for node in ['leftFrontWheel', 'rightBackWheel', 'rightFrontWheel', 'leftBackWheel']:
		rim = car.find('**/' + node)
		rim.setP(rim, spinSpeed * globalClock.getDt())
	if base.localAvatar.getDistance(car) < 10:
		if soundDriveByHonk.status() == soundDriveByHonk.READY:
			wantsToHonk = random.randint(0, 3)
			if wantsToHonk == 3:
				soundDriveByHonk.play()
			return task.cont
	elif base.localAvatar.getDistance(car) < 20:
		if soundDriveBy.status() == soundDriveBy.READY:
			soundDriveBy.play()
			return task.cont
	return task.cont

path2Duration = [100, 120, 120, 130]

moPath = Mopath.Mopath()
moPath.loadFile("new-cog-area/ct-citycar-drivepath-1.egg")
ival = MopathInterval(moPath, car, duration = 130)
ival.loop()

track = Parallel()
for node in ['leftFrontWheel', 'rightBackWheel', 'rightFrontWheel', 'leftBackWheel']:
	rim = car.find('**/' + node)
	#tire = car.find('**/' + i[:-1] + '2')
	track.append(LerpHprInterval(rim, duration = 0.1, hpr = (0, 360, 0), startHpr = (0, 0, 0)))
	#track.append(LerpHprInterval(tire, duration = 0.15, hpr = (0, 360, 0), startHpr = (0, 0, 0)))
#track.loop()

#car.find('**/wheelNode1').setX(

base.playSfx(soundCarRun, looping = 1)
taskMgr.add(__carDrive, "carDrive")

sphere = CollisionSphere(0, 0, 0, 2.5)
node = CollisionNode('cartsphere')
node.addSolid(sphere)
nodepath = car.attachNewNode(node)
nodepath.setZ(1.5)
nodepath.setSy(2.0)
nodepath.setSx(1.75)
#nodepath.show()

#self.notify.info("Anisotropic Filtering is on, applying to textures.")
for nodepath in render.findAllMatches('*'):
	try:
		for node in nodepath.findAllMatches('**'):
			try:
				node.findTexture('*').setAnisotropicDegree(8)
			except:
				pass
	except:
		continue

#base.startDirect()
#base.oobe()
base.run()

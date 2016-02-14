# Filename: DistributedCogOfficeBattle.py
# Created by:  blach (15Dec15)

from panda3d.core import Point3, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import LerpPosInterval, LerpHprInterval, Sequence, Wait, Func, LerpQuatInterval
from direct.fsm import ClassicFSM, State

from lib.coginvasion.nametag import NametagGlobals
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog import Dept
from ElevatorUtils import *
from ElevatorConstants import *
from CogOfficeConstants import *

PROPS = {'photo_frame':     'phase_7/models/props/photo_frame.egg',
        'rug':              'phase_3.5/models/modules/rug.bam',
        'couch_2person':    'phase_3.5/models/modules/couch_2person.bam',
        'LB_chairA':        'phase_11/models/lawbotHQ/LB_chairA.bam',
        'computer_monitor': 'phase_7/models/props/computer_monitor.egg',
        'coffee_cup':       'phase_7/models/props/coffee_cup.egg',
        'fax_paper':        'phase_7/models/props/fax_paper.egg',
        'phone':           ['phase_3.5/models/props/phone.bam',
                            'phase_3.5/models/props/receiver.bam'],
        'bookshelfB':       'phase_11/models/lawbotHQ/LB_bookshelfB.bam',
        'bookshelfA':       'phase_11/models/lawbotHQ/LB_bookshelfA.bam',
        'plant':            'phase_11/models/lawbotHQ/LB_pottedplantA.bam',
        'clock':            'phase_7/models/props/clock.egg',
        'meeting_table':    'phase_7/models/props/meeting_table.egg',
        'square_shadow':    'phase_3/models/props/square_drop_shadow.bam',
        'shadow':           'phase_3/models/props/drop_shadow.bam',
        'BR_sky':           'phase_3.5/models/props/BR_sky.bam'}

class Elevator:

    def __init__(self, elevatorMdl):
        self.elevatorMdl = elevatorMdl
        self.leftDoor = getLeftDoor(elevatorMdl)
        self.rightDoor = getRightDoor(elevatorMdl)

    def getRightDoor(self):
        return self.rightDoor

    def getLeftDoor(self):
        return self.leftDoor

    def getElevatorModel(self):
        return self.elevatorMdl

class DistributedCogOfficeBattle(DistributedObject):
    notify = directNotify.newCategory('DistributedCogOfficeBattle')
    CEILING_COLOR = (187.0 / 255, 174.0 / 255, 155.0 / 255)
    FLOOR_NAMES = {RECEPTION_FLOOR: 'Reception Floor', EXECUTIVE_FLOOR: 'Executive Floor'}
    UNIQUE_FLOORS = [1, 2, 3]
    UNIQUE_FLOOR_NAMES = {
        Dept.BOSS: {1: 'Stock Floor', 2: 'Board of Directors Floor', 3: 'Human Resources Floor'},
        Dept.SALES: {1: 'Marketing Floor', 2: 'Advertising Floor', 3: 'Telemarketing Floor'},
        Dept.LAW: {1: "Attorney's Floor", 2: "Paralegal Floor", 3: 'Document Management Floor'},
        Dept.CASH: {1: 'Accounting Floor', 2: 'Budgeting Floor', 3: 'Treasury Floor'}}
    DEPT_2_PAINTING = {Dept.BOSS: 'phase_7/maps/Bossbot_C_E_O_oil.jpg',
                       Dept.LAW: 'phase_7/maps/Lawbot_C_J_oil.jpg',
                       Dept.CASH: 'phase_7/maps/Cashbot_C_F_O_oil.jpg',
                       Dept.SALES: 'phase_7/maps/Sellbot_V_P_oil.jpg'}

    ROOM_DATA = {RECEPTION_FLOOR: {'props': [
                        ['photo_frame', -42.86, 0.72, 8.0, 0, 0, 90, 1],
                        ['rug', 0, 0, 0, 90, 0, 0, 1],
                        ['couch_2person', -23.68, 26.89, 0, 0, 0, 0, 1.25],
                        ['LB_chairA', -19.7, -6.5, 0, 180, 0, 0, 1],
                        ['LB_chairA', -24, -6.5, 0, 180, 0, 0, 1],
                        ['LB_chairA', 2.73, 19.46, 0, 330.95, 0, 0, 1],
                        ['computer_monitor', 0.19, 14.21, 3.01, 335.06, 0, 0, 1],
                        ['coffee_cup', -1.66, 15.88, 3.01, 0, 0, 0, 1],
                        ['phone', 3.17, 13.35, 2.97, 171.47, 0, 0, 1],
                        ['fax_paper', -3.32, 17.81, 3.01, 127.2, 0, 0, 1],
                        ['fax_paper', -3.32, 17.81, 3.005, 147.53, 0, 0, 1]
                    ],
                    'elevators': [
                        [0.74202, -9.50081, 0, 180, 0, 0],
                        [-39.49848, 20.74907, 0, 90, 0, 0]
                    ],
                    'room_mdl': 'phase_7/models/modules/cog_bldg_reception_flr.bam',
                    'grounds': ['**/floor']
                },
                EXECUTIVE_FLOOR: {'props': [
                        ['BR_sky', 0, 0, -100, 0, 0, 0, 1],
                        ['photo_frame', 16.26, 63.84, 8.34, 270.0, 0, 90.0, 1],
                        ['bookshelfA', -22.11, 49.88, 0.01, 90.0, 0, 0, 1.5],
                        ['bookshelfB', -22.11, 35, 0.01, 90, 0, 0, 1.5],
                        ['plant', 20.51, -5.13, 0, 0, 0, 0, 12],
                        ['rug', 0, 0, 0, 0, 0, 0, 1],
                        ['rug', 0, 52, 0, 0, 0, 0, 1],
                        ['clock', 23.68, 20.95, 9.67, 0, 0, 90, 1],
                        ['LB_chairA', 20.7, 8.14, 0, 270, 0, 0, 1],
                        ['computer_monitor', 13.73, 8.17, 3.99, 270, 0, 0, 1],
                        ['coffee_cup', 14.25, 10.65, 3.99, 78.69, 0, 0, 1],
                        ['phone', 14.20, 5.29, 3.99, 95.96, 0, 0, 1.2],
                        ['fax_paper', 14.54, 13.34, 4.01, 63.43, 0, 0, 1],
                        ['fax_paper', 14.43, 0.72, 4.01, 270, 0, 0, 1],
                        ['fax_paper', 16.8, 1.14, 4.01, 118.61, 0, 0, 1],
                        ['meeting_table', -12.7, 5.94, 0, 0, 0, 0, 1],
                        ['LB_chairA', -22.02, 1.57, 0, 90.0, 0, 0, 1],
                        ['LB_chairA', -22.02, 10.23, 0, 90.0, 0, 0, 1],
                        ['LB_chairA', -13.13, 19.73, 0, 0, 0, 0, 1],
                        ['square_shadow', -12.7, 5.94, 0.01, 0, 0, 0, Point3(2, 3.5, 1)],
                        ['fax_paper', -16.71, 1.57, 3.4, 270, 0, 0, 1],
                        ['fax_paper', -16.71, 10.23, 3.4, 270, 0, 0, 1],
                        ['fax_paper', -13.44, 14.8, 3.41, 180, 0, 0, 1],
                        ['fax_paper', -13.44, 14.8, 3.4, 150, 0, 0, 1]
                    ],
                    'elevators': [
                        [0.23007, 60.47556, 0, 0, 0, 0],
                        [0.74202, -9.50081, 0, 180, 0, 0]
                    ],
                    'room_mdl': 'phase_7/models/modules/cog_bldg_executive_flr.bam',
                    'grounds': ['**/floor']
                }
    }

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.currentFloor = None
        self.numFloors = None
        self.dept = None
        self.deptClass = None
        self.floorModel = None
        self.exteriorZoneId = None
        self.bldgDoId = None
        self.avatars = None
        self.props = []
        self.elevators = []
        self.elevatorResponses = 0
        self.openSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_open.mp3')
        self.closeSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_close.mp3')
        self.rideElevatorMusic = base.loadMusic('phase_7/audio/bgm/tt_elevator.mid')
        self.bottomFloorsMusic = base.loadMusic('phase_7/audio/bgm/encntr_general_bg_indoor.mid')
        self.topFloorMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.mid')
        self.intermissionMusic = base.loadMusic('phase_7/audio/bgm/encntr_toon_winning_indoor.mid')
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeBattle', [State.State('off', self.enterOff, self.exitOff),
         State.State('floorIntermission', self.enterFloorIntermission, self.exitFloorIntermission),
         State.State('battle', self.enterBattle, self.exitBattle),
         State.State('rideElevator', self.enterRideElevator, self.exitRideElevator),
         State.State('faceOff', self.enterFaceOff, self.exitFaceOff),
         State.State('victory', self.enterVictory, self.exitVictory)], 'off', 'off')
        self.fsm.enterInitialState()

    def enterVictory(self, ts):
        self.cr.playGame.getPlace().fsm.request('stop')
        base.localAvatar.b_setAnimState('win')
        base.taskMgr.doMethodLater(5.0, self.victoryTask, self.uniqueName('victoryTask'))

    def victoryTask(self, task):
        requestStatus = {
            'zoneId': self.exteriorZoneId,
            'hoodId': self.cr.playGame.hood.id,
            'bldgDoId': self.bldgDoId,
            'loader': 'townLoader',
            'where': 'street',
            'world': CIGlobals.CogTropolis,
            'shardId': None,
            'wantLaffMeter': 1,
            'avId': base.localAvatar.doId,
            'how': 'elevatorIn'
        }
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])
        return task.done

    def exitVictory(self):
        base.taskMgr.remove(self.uniqueName('victoryTask'))

    def setExteriorZoneId(self, zoneId):
        self.exteriorZoneId = zoneId

    def setBldgDoId(self, doId):
        self.bldgDoId = doId

    def d_readyForNextFloor(self):
        self.sendUpdate('readyForNextFloor')

    def elevatorReady(self):
        # We have to wait until all of our elevators are ready before
        # telling the AI that we're ready to begin the battle.
        self.elevatorResponses += 1
        if self.elevatorResponses >= len(self.elevators):
            self.sendUpdate('readyToStart')

    def setNumFloors(self, num):
        self.numFloors = num

    def setState(self, state, timestamp):
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def setAvatars(self, avatars):
        self.avatars = avatars

    def setDept(self, dept):
        self.dept = dept
        if dept == 'c':
            self.deptClass = Dept.BOSS
        elif dept == 'l':
            self.deptClass = Dept.LAW
        elif dept == 's':
            self.deptClass = Dept.SALES
        elif dept == 'm':
            self.deptClass = Dept.CASH

    def enterOff(self, ts = 0):
        base.transitions.fadeScreen(1)

    def exitOff(self):
        base.transitions.noTransitions()

    def getPoints(self, name):
        if self.currentFloor in self.UNIQUE_FLOORS:
            points = POINTS[self.deptClass][self.currentFloor][name]
        else:
            points = POINTS[self.currentFloor][name]
        return points

    def enterFaceOff(self, ts):
        base.localAvatar.attachCamera()
        camera.lookAt(base.localAvatar.smartCamera.getLookAtPoint())
        camera.setY(camera.getY() + 5)
        self.faceOffTracks = []
        for i in xrange(len(self.avatars)):
            avId = self.avatars[i]
            toon = self.cr.doId2do.get(avId)
            if toon:
                toon.stopSmooth()
                toon.wrtReparentTo(render)
                points = self.getPoints('faceoff')
                point = points[i]
                pos = Point3(point[0], point[1], point[2])
                hpr = Vec3(point[3], point[4], point[5])
                toon.headsUp(pos)
                track = Sequence(
                    Func(toon.setAnimState, 'run'),
                    LerpPosInterval(toon, duration = 1.0, pos = pos,
                        startPos = toon.getPos(render)),
                    Func(toon.setAnimState, 'walk'),
                    LerpQuatInterval(toon, duration = 1.0, hpr = hpr,
                        startHpr = lambda toon = toon: toon.getHpr(render)),
                    Func(toon.setAnimState, 'neutral'))
                self.faceOffTracks.append(track)
                track.start(ts)

    def exitFaceOff(self):
        for track in self.faceOffTracks:
            track.finish()
        del self.faceOffTracks

    def enterRideElevator(self, ts):
        elevator = self.elevators[0]
        base.camLens.setFov(CIGlobals.DefaultCameraFov)
        NametagGlobals.setWant2dNametags(False)
        camera.reparentTo(elevator.getElevatorModel())
        camera.setHpr(180, 0, 0)
        self.elevatorTrack = getRideElevatorInterval()
        self.elevatorTrack.append(getOpenInterval(self, elevator.getLeftDoor(), elevator.getRightDoor(), self.openSfx, None))
        self.elevatorTrack.start(ts)
        base.transitions.noTransitions()
        base.playMusic(self.rideElevatorMusic, volume = 0.8, looping = 1)

    def exitRideElevator(self):
        if hasattr(self, 'elevatorTrack'):
            self.elevatorTrack.finish()
            del self.elevatorTrack
        self.rideElevatorMusic.stop()
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
        NametagGlobals.setWant2dNametags(True)

    def enterBattle(self, ts):
        if self.currentFloor < self.numFloors - 1:
            song = self.bottomFloorsMusic
        else:
            song = self.topFloorMusic
        base.playMusic(song, looping = 1, volume = 0.8)
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')
        taskMgr.add(self.monitorHP, self.uniqueName('monitorHP'))

    def monitorHP(self, task):
        if base.localAvatar.getHealth() < 1:
            taskMgr.doMethodLater(7.0, self.diedTask, self.uniqueName('diedTask'))
            return task.done
        return task.cont

    def diedTask(self, task):
        self.sendUpdate('iAmDead')
        return task.done

    def exitBattle(self):
        self.bottomFloorsMusic.stop()
        taskMgr.remove(self.uniqueName('monitorHP'))

    def enterFloorIntermission(self, ts):
        self.topFloorMusic.stop()
        base.playMusic(self.intermissionMusic, looping = 1, volume = 0.8)

    def exitFloorIntermission(self):
        self.intermissionMusic.stop()

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        base.setBackgroundColor(self.CEILING_COLOR)
        self.cr.playGame.hood.stopSuitEffect()
        self.cr.playGame.hood.sky.hide()
        self.loadElevators()

    def disable(self):
        taskMgr.remove(self.uniqueName('diedTask'))
        taskMgr.remove(self.uniqueName('monitorHP'))
        self.fsm.requestFinalState()
        del self.fsm
        if self.cr.playGame.hood is not None:
            self.cr.playGame.hood.startSuitEffect()
            self.cr.playGame.hood.sky.show()
        self.cleanupFloor()
        self.cleanupElevators()
        self.props = None
        self.currentFloor = None
        self.floorModel = None
        self.avatars = None
        self.elevators = None
        self.dept = None
        self.deptClass = None
        self.openSfx = None
        self.closeSfx = None
        self.rideElevatorMusic = None
        self.bottomFloorsMusic = None
        self.intermissionMusic = None
        self.bldgDoId = None
        self.exteriorZoneId = None
        if self.topFloorMusic:
            self.topFloorMusic.stop()
            self.topFloorMusic = None
        base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
        DistributedObject.disable(self)

    def loadFloor(self, floorNum):
        self.cleanupFloor()
        self.currentFloor = floorNum
        self.loadRoom()
        self.loadProps()
        self.repositionElevators()

    def cleanupFloor(self):
        for prop in self.props:
            prop.removeNode()
        self.props = []
        if self.floorModel:
            self.floorModel.removeNode()
            self.floorModel = None

    def cleanupElevators(self):
        for elevator in self.elevators:
            elevator.getElevatorModel().removeNode()
        self.elevators = []

    def getRoomData(self, name):
        if self.currentFloor in self.UNIQUE_FLOORS:
            dataList = self.ROOM_DATA[self.deptClass][self.currentFloor][name]
        else:
            dataList = self.ROOM_DATA[self.currentFloor][name]
        return dataList

    def loadRoom(self):
        path = self.getRoomData('room_mdl')
        grounds = self.getRoomData('grounds')
        self.floorModel = loader.loadModel(path)
        self.floorModel.reparentTo(render)
        for ground in grounds:
            self.floorModel.find(ground).setBin('ground', 18)

    def loadProps(self):
        dataList = self.getRoomData('props')
        for propData in dataList:
            name = propData[0]
            otherProps = []
            if isinstance(PROPS[name], list):
                for i in xrange(len(PROPS[name])):
                    if i == 0:
                        continue
                    path = PROPS[name][i]
                    otherProps.append(path)
            x, y, z = propData[1], propData[2], propData[3]
            h, p, r = propData[4], propData[5], propData[6]
            scale = propData[7]
            if isinstance(PROPS[name], list):
                propMdl = loader.loadModel(PROPS[name][0])
            else:
                propMdl = loader.loadModel(PROPS[name])
            propMdl.reparentTo(render)
            propMdl.setPosHpr(x, y, z, h, p, r)
            propMdl.setScale(scale)
            if name == 'photo_frame':
                propMdl.find('**/photo').setTexture(loader.loadTexture(self.DEPT_2_PAINTING[self.deptClass]), 1)
            for oPropPath in otherProps:
                oPropMdl = loader.loadModel(oPropPath)
                oPropMdl.reparentTo(propMdl)
            self.props.append(propMdl)

    def loadElevators(self):
        for i in xrange(2):
            elevMdl = loader.loadModel('phase_4/models/modules/elevator.bam')
            elevMdl.reparentTo(render)
            elevator = Elevator(elevMdl)
            self.elevators.append(elevator)

    def repositionElevators(self):
        dataList = self.getRoomData('elevators')
        for i in xrange(len(dataList)):
            x, y, z, h, p, r = dataList[i]
            elevMdl = self.elevators[i].getElevatorModel()
            elevMdl.setPosHpr(x, y, z, h, p, r)
            npc = elevMdl.findAllMatches('**/floor_light_?;+s')
            for i in xrange(npc.getNumPaths()):
                np = npc.getPath(i)
                floor = int(np.getName()[-1:]) - 1
                if floor < self.numFloors:
                    np.setColor(LIGHT_OFF_COLOR)
                else:
                    np.hide()
                if self.currentFloor == floor:
                    np.setColor(LIGHT_ON_COLOR)

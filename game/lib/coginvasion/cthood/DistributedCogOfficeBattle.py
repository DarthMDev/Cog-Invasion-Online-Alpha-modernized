# Filename: DistributedCogOfficeBattle.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm import ClassicFSM, State

PROPS = {'photo_frame':     'cog-bldg-modles/photo_frame.egg',
        'rug':              'phase_3.5/models/modules/rug.bam',
        'couch_2person':    'phase_3.5/models/modules/couch_2person.bam',
        'LB_chairA':        'phase_11/models/lawbotHQ/LB_chairA.bam',
        'computer_monitor': 'cog-bldg-modles/computer_monitor.egg',
        'coffee_cup':       'cog-bldg-modles/coffee_cup.egg',
        'fax_paper':        'cog-bldg-modles/fax_paper.egg',
        'phone':           ['phase_3.5/models/props/phone.bam',
                            'phase_3.5/models/props/receiver.bam']}

class DistributedCogOfficeBattle(DistributedObject):
    notify = directNotify.newCategory('DistributedCogOfficeBattle')
    FLOOR_NAMES = {0: 'Reception Floor', 4: 'Executive Floor'}
    UNIQUE_FLOORS = [1, 2, 3]
    UNIQUE_FLOOR_NAMES = {
        Dept.BOSS: {1: 'Stock Floor', 2: 'Board of Directors Floor', 3: 'Human Resources Floor'},
        Dept.SALES: {1: 'Marketing Floor', 2: 'Advertising Floor', 3: 'Telemarketing Floor'},
        Dept.LAW: {1: "Attorney's Floor", 2: "Paralegal Floor", 3: 'Document Management Floor'},
        Dept.CASH: {1: 'Accounting Floor', 2: 'Budgeting Floor', 3: 'Treasury Floor'}}

    ROOM_DATA = {0: {'props': [
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
                    ]
                }
    }

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.currentFloor = None
        self.dept = None
        self.floorModel = None
        self.props = []
        self.elevatorModels = []
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeBattle', [State.State('off', self.enterOff, self.exitOff),
         State.State('floorIntermission', self.enterFloorIntermission, self.exitFloorIntermission),
         State.State('battle', self.enterBattle, self.exitBattle),
         State.State('rideElevator', self.enterRideElevator, self.exitRideElevator)], 'off', 'off')
        self.fsm.enterInitialState()

    def loadProps(self):
        if self.currentFloor in self.UNIQUE_FLOORS:
            dataList = self.ROOM_DATA[self.deptClass][self.currentFloor]
        else:
            dataList = self.ROOM_DATA[self.currentFloor]
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
            propMdl = loader.loadModel(PROPS[name])
            propMdl.reparentTo(render)
            propMdl.setPosHprScale(x, y, z, h, p, r, scale, scale, scale)
            for oPropPath in otherProps:
                oPropMdl = loader.loadModel(oPropPath)
                oPropMdl.reparentTo(propMdl)
            self.props.append(propMdl)

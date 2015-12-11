"""

  Filename: SuitPathBehavior.py
  Created by: DecodedLogic (03Sep15)

"""

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval

import random

class Node:

    def __init__(self, g_cost, h_cost, key, point):
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.key = key
        self.point = point
        self.parent = None

class SuitPathBehavior(SuitBehaviorBase):

    def __init__(self, suit, exitOnWalkFinish = True):
        SuitBehaviorBase.__init__(self, suit)
        self.walkTrack = None
        self.exitOnWalkFinish = exitOnWalkFinish
        self.isEntered = 0

    def unload(self):
        SuitBehaviorBase.unload(self)
        self.clearWalkTrack()
        del self.exitOnWalkFinish
        del self.walkTrack

    def createPath(self, pathKey = None, durationFactor = 0.2, fromCurPos = False):
        currentPathQueue = self.suit.getCurrentPathQueue()
        currentPath = self.suit.getCurrentPath()
        if pathKey == None and not len(currentPathQueue):
            pathKeyList = CIGlobals.SuitPathData[self.suit.getHood()][self.suit.getCurrentPath()]
            pathKey = random.choice(pathKeyList)
        elif len(currentPathQueue):
            pathKey = currentPathQueue[0]
            currentPathQueue.remove(pathKey)
        endIndex = CIGlobals.SuitSpawnPoints[self.suit.getHood()].keys().index(pathKey)
        path = CIGlobals.SuitSpawnPoints[self.suit.getHood()][pathKey]
        self.clearWalkTrack()
        if not currentPath or fromCurPos:
            startIndex = -1
        else:
            oldPath = currentPath
            startIndex = CIGlobals.SuitSpawnPoints[self.suit.getHood()].keys().index(oldPath)
        self.suit.currentPath = pathKey
        startPos = self.suit.getPos(render)
        pathName = self.suit.uniqueName('suitPath')
        self.walkTrack = NPCWalkInterval(self.suit, path, startPos = startPos,
            name = pathName, durationFactor = durationFactor, fluid = 1
        )
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.startFollow()
        self.suit.b_setSuitState(1, startIndex, endIndex)

    def getDistance(self, point1, point2):
        return (point1.getXy() - point2.getXy()).length()

    def getPath(self, start_key, target_key, nodes):
        path = []

        for node in nodes:
            if node.key == start_key:
                start_node = node
            elif node.key == target_key:
                target_node = node

        current_node = target_node
        while (current_node.parent != start_node):
            path.append(current_node.key)
            current_node = current_node.parent
        path.append(start_key)
        return list(reversed(path))

    def findPath(self, area, start_key, target_key):
        start_point = CIGlobals.SuitSpawnPoints[area][start_key]
        target_point = CIGlobals.SuitSpawnPoints[area][target_key]

        nodes = []
        open_nodes = []
        closed_nodes = []

        for key, point in CIGlobals.SuitSpawnPoints[area].items():
            g_cost = self.getDistance(point, start_point)
            h_cost = self.getDistance(point, target_point)
            node = Node(g_cost, h_cost, key, point)
            nodes.append(node)

        for node in nodes:
            if node.key == start_key:
                open_nodes.append(node)

        while len(open_nodes):
            f_cost_list = []
            for node in open_nodes:
                f_cost_list.append(node.f_cost)

            lowest_f_cost = min(f_cost_list)

            current = None
            for node in open_nodes:
                if lowest_f_cost == node.f_cost:
                    current = node

            open_nodes.remove(current)
            closed_nodes.append(current)

            if current.key == target_key:
                return self.getPath(start_key, target_key, nodes)

            neighbor_keys = CIGlobals.SuitPathData[area][current.key]
            for neighbor_key in neighbor_keys:

                isClosed = False
                for node in closed_nodes:
                    if node.key == neighbor_key:
                        isClosed = True
                        break
                if isClosed:
                    continue

                neighbor = None
                for node in nodes:
                    if node.key == neighbor_key:
                        neighbor = node
                        break

                nm_cost_2_neighbor = current.g_cost + self.getDistance(current.point, neighbor.point)
                if (not neighbor in open_nodes) or \
                (nm_cost_2_neighbor < neighbor.g_cost):
                    neighbor.g_cost = nm_cost_2_neighbor
                    neighbor.h_cost = self.getDistance(target_point, neighbor.point)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current

                    if not neighbor in open_nodes:
                        open_nodes.append(neighbor)

    def clearWalkTrack(self):
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.clearToInitial()
            self.walkTrack = None
            if hasattr(self, 'suit'):
                self.suit.d_stopMoveInterval()

    def startFollow(self):
        self.suit.b_setAnimState('walk')
        if self.walkTrack:
            self.acceptOnce(self.walkTrack.getName(), self._walkDone)
            self.walkTrack.start()

    def _walkDone(self):
        self.clearWalkTrack()
        if not self.suit.isDead():
            self.suit.b_setAnimState('neutral')
            if self.exitOnWalkFinish == True:
                self.exit()

    def getWalkTrack(self):
        return self.walkTrack

    def isWalking(self):
        if self.walkTrack:
            return self.walkTrack.isPlaying()
        return False

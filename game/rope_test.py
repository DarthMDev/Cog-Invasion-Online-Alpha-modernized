from panda3d.core import loadPrcFile
loadPrcFile('config/config_client.prc')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.showutil.Rope import Rope

phone = loader.loadModel("phase_3.5/models/props/phone.bam")
phone.reparentTo(render)
receiver = loader.loadModel("phase_3.5/models/props/receiver.bam")
#receiver.setX(20)
receiver.reparentTo(render)
line_node = phone.attachNewNode('line_node') # Where the rope comes out


rope = Rope()
rope.ropeNode.setUseVertexColor(1)
rope.ropeNode.setUseVertexThickness(0)
rope.setup(3, ({'node': phone, 'point': (0, 0, 0.2), 'color': (0, 0, 0, 1), 'thickness': 1.5}, {'node': phone, 'point': (-0.5, 0, 0), 'color': (0, 0, 0, 1), 'thickness': 1.5}, {'node': receiver, 'point': (-0.15, 0.25, 0.5), 'color': (0, 0, 0, 1), 'thickness': 1.5}), [])
rope.reparentTo(render)

from direct.interval.IntervalGlobal import *
phoneIval = LerpPosInterval(phone, duration = 5.0, pos = (0, 0, 20.0), startPos = phone.getPos(render))
#phoneIval.start()

base.run()

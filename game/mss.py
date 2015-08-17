from panda3d.core import *
loadPrcFileData('', 'audio-library-name p3miles_audio')
loadPrcFileData('', 'load-display pandagl')
from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from direct.interval.IntervalGlobal import *

array = ['/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/BossBot_CEO_v1.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/BossBot_CEO_v2.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_4/audio/bgm/MG_Pairing.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_12/audio/bgm/Bossbot_Entry_v1.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_4/audio/bgm/MG_Pairing.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/tt_elevator.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/encntr_suit_winning_indoor.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_3.5/audio/bgm/encntr_general_bg.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_4/audio/bgm/firework_music.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_4/audio/bgm/TC_nbrhood.mid',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_3.5/audio/bgm/encntr_nfsmw_bg_3.ogg',
	'/c/Users/Brian/Documents/panda3d/build_test/phase_7/audio/bgm/encntr_suit_winning_indoor.mid']
currentSong = -1
#music = loader.loadMusic(array[currentSong])
#music.setLoop(False)
#music.play()

music = None

def stopCurrentMusic():
	music.stop()
	
def playNextSong():
	global music
	global currentSong
	if music:
		music.stop()
	currentSong += 1
	music = loader.loadMusic(array[currentSong])
	music.setLoop(True)
	music.play()

base.accept("s", stopCurrentMusic)
base.accept("p", playNextSong)

#base.accept("PandaPaused", base.enableMusic, [False])
#base.accept("PandaRestarted", base.enableMusic, [True])

base.run()

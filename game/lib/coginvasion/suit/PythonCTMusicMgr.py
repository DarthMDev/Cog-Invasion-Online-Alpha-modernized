# Filename: PythonCTMusicMgr.py
# Created by:  blach (28Jun16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

import ccoginvasion

import random

class PythonCTMusicManager(DirectObject, ccoginvasion.CTMusicManager):
    notify = directNotify.newCategory("PythonCTMusicManager")

    # Wait this long to begin monitoring our situation number so
    # the intro clip has time to play.
    TimeUntilBeginMonitoring = 10.0

    ArrestingYouRange = [-50, -41]
    GettingWorseRange = [-40, -21]
    FiftyFiftyRange = [-20, 20]
    RunningAwayRange = [21, 35]
    HSpdClDwnRange = [36, 45]
    StcClDwnRange = [46, 50]

    StyleChangeTRange = [15, 30]

    IntroOrchestraFromLocatedStartPoint = [43, 44]

    def __init__(self, suitMgr):
        # Initialize C++ layer.
        ccoginvasion.CTMusicManager.__init__(self)

        self.suitMgr = suitMgr

        # We're gonna follow the nfsmw way of deciding on the music.
        # Right now, at 0, we're in the middle of the pursuit bar, which means
        # everything is like going even (50/50). If our situationNumber becomes higher than 0,
        # Things are getting worse. (getting_worse). If it gets up to 50: arresting_you.
        # Our situation number will rise if cogs are attacking us, or we are near a lot of cogs.
        # Also it will rise if our health is low.
        # If our number goes below 0, we have the advantage. We are running away from the cogs
        # or there aren't a lot of cogs near us at all.
        self.situationNumber = 0.0

        self.lastStyleChangeT = 0.0
        self.styleChangeIval = 0.0

        self.shouldSwitchToIntro = False
        self.switchToIntroPoint = 0

    @staticmethod
    def getCogInRangeDistance():
        # What would we consider in range?
        return 20.0

    @staticmethod
    def getCogAttackingEvent():
        return 'CogEvent::attacking'

    def __handleCogAttacking(self):
        # A cog is attacking me. Things are getting worse...
        self.situationNumber -= 5.0

    @staticmethod
    def getCogInRangeEvent():
        return 'CogEvent::in-range'

    def __handleCogInRange(self):
        # A cog might be chasing me.
        self.situationNumber -= 2.5

    @staticmethod
    def getCogOutOfRangeEvent():
        return 'CogEvent::out-of-range'

    def __handleCogOutOfRange(self):
        # A cog went out of range... phew!
        self.situationNumber += 3.0

    @staticmethod
    def getCogDiedEvent():
        return 'CogEvent::died'

    def __handleCogDied(self):
        # A cog died! Big relief!
        self.situationNumber += 5.0

    @staticmethod
    def getToonDiedEvent():
        return 'ToonEvent::buddy-died'

    def __handleToonDied(self):
        # One of my friends died!
        self.situationNumber -= 10.0

    @staticmethod
    def getLocalAvHurtEvent():
        return 'ToonEvent::local-av-hurt'

    def __handleLocalAvHurt(self):
        # I'm hurt!
        self.situationNumber -= 5.0

    def __is_in_range(self, therange):
        return (self.situationNumber >= therange[0] and self.situationNumber <= therange[1])

    def get_curr_style(self):
        splitName = self.get_clip_name().split('_')
        if "orchestra" in splitName or "base" in splitName:
            return "_" + splitName[len(splitName) - 1]
        else:
            return "_orchestra"

    def pick_style(self):
        return random.choice(["_base", "_orchestra"])

    def __monitor_situation_task(self, task):
        if self.situationNumber > 50.0:
            self.situationNumber = 50.0
        elif self.situationNumber < -50.0:
            self.situationNumber = -50.0

        # Gradually move the situation back to 0.
        if self.situationNumber > 0.0:
            self.situationNumber -= 5.0 * globalClock.getDt()
        elif self.situationNumber < 0.0:
            self.situationNumber += 5.0 * globalClock.getDt()

        currTime = globalClock.getFrameTime()

        shouldChangeStyle = (currTime - self.lastStyleChangeT) >= self.styleChangeIval

        extension = self.pick_style()

        #print self.situationNumber

        if self.__is_in_range(PythonCTMusicManager.FiftyFiftyRange):
            # It's 50/50
            self.set_clip_request("5050" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("5050" + extension)

        elif self.__is_in_range(PythonCTMusicManager.RunningAwayRange):
            self.set_clip_request("running_away" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("running_away" + extension)

        elif self.__is_in_range(PythonCTMusicManager.GettingWorseRange):
            self.set_clip_request("getting_worse" + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("getting_worse" + extension)

        elif self.__is_in_range(PythonCTMusicManager.ArrestingYouRange):
            self.set_clip_request("arresting_you")

        elif self.__is_in_range(PythonCTMusicManager.HSpdClDwnRange):
            self.set_clip_request('high_speed_cooldown' + self.get_curr_style())
            if shouldChangeStyle:
                self.set_clip_request("high_speed_cooldown" + extension)

        elif self.__is_in_range(PythonCTMusicManager.StcClDwnRange):
            self.set_clip_request('static_cooldown')

        if shouldChangeStyle:
            SCTR = PythonCTMusicManager.StyleChangeTRange
            self.styleChangeIval = random.randint(SCTR[0], SCTR[1])
            self.lastStyleChangeT = globalClock.getFrameTime()

        return task.cont

    def start_music(self):
        ccoginvasion.CTMusicManager.start_music(self)

        self.lastStyleChangeT = globalClock.getFrameTime()

        SCTR = PythonCTMusicManager.StyleChangeTRange
        self.styleChangeIval = random.randint(SCTR[0], SCTR[1])

        self.accept(PythonCTMusicManager.getCogDiedEvent(), self.__handleCogDied)
        self.accept(PythonCTMusicManager.getCogInRangeEvent(), self.__handleCogInRange)
        self.accept(PythonCTMusicManager.getCogAttackingEvent(), self.__handleCogAttacking)
        self.accept(PythonCTMusicManager.getCogOutOfRangeEvent(), self.__handleCogOutOfRange)

        self.accept(PythonCTMusicManager.getToonDiedEvent(), self.__handleToonDied)
        self.accept(PythonCTMusicManager.getLocalAvHurtEvent(), self.__handleLocalAvHurt)

        base.taskMgr.doMethodLater(
            PythonCTMusicManager.TimeUntilBeginMonitoring, self.__monitor_situation_task,
            self.suitMgr.uniqueName('monitorSituationTask'))

    def handle_part_done(self, partIndex):
        # PartIndex = the index of the part that just finished
        if self.shouldSwitchToIntro:
            if self.switchToIntroPoint == partIndex:
                self.set_clip_request("intro_orchestra_from_located")
                self.shouldSwitchToIntro = False
                self.switchToIntroPoint = 0

        ccoginvasion.CTMusicManager.handle_part_done(self, partIndex)

    def play_located(self):
        # This is basically an intro but to a new cog round.
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        self.shouldSwitchToIntro = random.choice([True, False])
        if self.shouldSwitchToIntro:
            self.switchToIntroPoint = random.choice(self.IntroOrchestraFromLocatedStartPoint)
        self.set_clip_request("located" + self.pick_style())
        base.taskMgr.doMethodLater(
            PythonCTMusicManager.TimeUntilBeginMonitoring, self.__monitor_situation_task,
            self.suitMgr.uniqueName('monitorSituationTask'))

    def play_cooldown(self):
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))
        self.set_clip_request('static_cooldown')

    def stop_music(self):
        self.ignore(PythonCTMusicManager.getCogDiedEvent())
        self.ignore(PythonCTMusicManager.getCogInRangeEvent())
        self.ignore(PythonCTMusicManager.getCogAttackingEvent())
        self.ignore(PythonCTMusicManager.getCogOutOfRangeEvent())
        self.ignore(PythonCTMusicManager.getToonDiedEvent())
        self.ignore(PythonCTMusicManager.getLocalAvHurtEvent())

        self.stop_clip()
        base.taskMgr.remove(self.suitMgr.uniqueName('monitorSituationTask'))

    def cleanup(self):
        self.shouldSwitchToIntro = None
        self.switchToIntroPoint = None
        self.suitMgr = None
        self.lastStyleChangeT = None
        self.styleChangeIval = None
        self.situationNumber = None

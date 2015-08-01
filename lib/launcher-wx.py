# Filename: launcher.py
# Created by:  blach (09Nov14)

import sys
import os
import subprocess
import hashlib
from panda3d.core import *
loadPrcFileData('startup', 'window-type none')
#loadPrcFileData('startup', 'load-display pandagl')
loadPrcFileData('startup', 'default-directnotify-level info')
from direct.showbase.ShowBase import ShowBase
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.distributed.PyDatagram import PyDatagram
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task
import wx
base = ShowBase()
base.startWx()

CLIENT_MD5 = 0
SERVER_MD5 = 1
ACC_VALIDATE = 10
ACC_INVALID = 11
ACC_VALID = 12
ACC_CREATE = 13
ACC_CREATED = 14
ACC_EXISTS = 15
DL_TIME_REPORT = 16
LAUNCHER_VERSION = 17
LAUNCHER_GOOD = 18
LAUNCHER_BAD = 19
FETCH_DL_LIST = 20
DL_LIST = 21

baseLink = ""
fileNames = []

class Launcher(wx.Frame):
    notify = directNotify.newCategory("Launcher")
    appTitle = "Cog Invasion Launcher"
    loginServer_port = 7033
    Server_host = "localhost"
    timeout = 2000
    version = 1.0
    helpVideoLink = "http://download.coginvasion.com/videos/ci_launcher_crash_help.mp4"

    def __init__(self):
        wx.Frame.__init__(self, None, 'Cog Invasion Launcher')
        self.wx = base.wxApp
        self.tk.geometry("262x125+500+200")
        self.tk.title(self.appTitle)
        self.tk.resizable(0, 0)
        self.tk.iconbitmap('icon.ico')
        self.launcherFSM = ClassicFSM('launcher', [State('menu', self.enterMenu, self.exitMenu, ['updateFiles', 'accCreate']),
            State('fetch', self.enterFetch, self.exitFetch, ['menu']),
            State('validate', self.enterValidate, self.exitValidate, ['fetch']),
            State('connect', self.enterConnect, self.exitConnect, ['validate']),
            State('accCreate', self.enterAccCreate, self.exitAccCreate, ['submitAcc', 'menu']),
            State('submitAcc', self.enterSubmitAcc, self.exitSubmitAcc, ['menu', 'accCreate']),
            State('login', self.enterLogin, self.exitLogin, ['play', 'menu']),
            State('play', self.enterPlay, self.exitPlay, ['off']),
            State('updateFiles', self.enterUpdateFiles, self.exitUpdateFiles, ['login']),
            State('off', self.enterOff, self.exitOff)], 'off', 'off')
        self.launcherFSM.enterInitialState()
        self.loginUserName = StringVar()
        self.loginPassword = StringVar()
        self.downloadTime = {}
        self.__initConnectionManagers()
        self.checkHasFolder("logs")
        self.checkHasFolder("screenshots")
        self.checkHasFolder("config")
        self.launcherFSM.request('connect')

    def __initConnectionManagers(self):
        self.cMgr = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cMgr, 0)
        self.cWriter = ConnectionWriter(self.cMgr, 0)
        self.http = HTTPClient()
        self.rf = Ramfile()
        self.channel = self.http.makeChannel(True)

    def checkHasFolder(self, folderName):
        if not os.path.isdir(folderName):
            os.mkdir(folderName)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterValidate(self):
        self.infoLbl = Label(self.tk, text = "Validating...")
        self.infoLbl.pack()
        self.tk.update()
        self.badLauncherMsg = None
        dg = PyDatagram()
        dg.addUint16(LAUNCHER_VERSION)
        dg.addFloat64(self.version)
        self.cWriter.send(dg, self.Connection)

    def __handleBadLauncher(self):
        self.badLauncherMsg = tkMessageBox.showwarning(parent = self.tk, title = "Error", message = "This launcher is out of date. Please go to coginvasion.com and download the latest launcher.")
        sys.exit()

    def exitValidate(self):
        self.infoLbl.pack_forget()
        del self.infoLbl
        if self.badLauncherMsg:
            self.badLauncherMsg.destroy()
            del self.badLauncherMsg

    def enterFetch(self):
        self.infoLbl = Label(self.tk, text = "Fetching download list...")
        self.infoLbl.pack()
        self.tk.update()
        dg = PyDatagram()
        dg.addUint16(FETCH_DL_LIST)
        self.cWriter.send(dg, self.Connection)

    def exitFetch(self):
        self.infoLbl.pack_forget()
        del self.infoLbl

    def enterUpdateFiles(self):
        self.currentFile = -1
        self.filesDownloaded = 0
        self.currentMD5 = ""
        self.title = Label(self.tk, text = "Updating files...\n")
        self.title.pack()
        self.infoLbl = Label(self.tk)
        self.infoLbl.pack()
        self.progBar = ttk.Progressbar(orient = "horizontal", length = 100, mode = "determinate")
        self.progBar.pack()
        self.nextFile()

    def nextFile(self):
        self.currentFile += 1
        if self.currentFile > len(fileNames) - 1:
            if self.filesDownloaded > 0:
                self.reportDownloadTimes()
            self.launcherFSM.request('login')
            return
        self.infoLbl.config(text = "File %s of %s" % (self.currentFile + 1, len(fileNames)))
        fileName = fileNames[self.currentFile]
        print fileName
        if os.path.isfile(fileName):
            self.currentMD5 = hashlib.md5(open(fileName).read()).hexdigest()
            self.sendMD5(fileName)
        else:
            self.downloadFile()

    def reportDownloadTimes(self):
        print "----------DOWNLOAD TIMES----------"
        totalTime = 0
        for k, v in self.downloadTime.iteritems():
            print fileNames[k] + ": " + str(self.downloadTime[k]) + " seconds."
            totalTime += self.downloadTime[k]
        print "Total time: " + str(totalTime) + " seconds."
        dg = PyDatagram()
        dg.addUint16(DL_TIME_REPORT)
        dg.addFloat64(totalTime)
        self.cWriter.send(dg, self.Connection)

    def startTrackingDownloadTime(self):
        self.downloadTime[self.currentFile] = 0.0
        self.currentDownloadStartTime = globalClock.getFrameTime()

    def stopTrackingDownloadTime(self):
        self.downloadTime[self.currentFile] = globalClock.getFrameTime() - self.currentDownloadStartTime
        del self.currentDownloadStartTime

    def downloadFile(self):
        name = fileNames[self.currentFile]
        fullLink = baseLink + name
        self.channel.beginGetDocument(DocumentSpec(fullLink))
        self.channel.downloadToFile(name)
        taskMgr.add(self.__downloadTask, "downloadTask")
        self.startTrackingDownloadTime()

    def __downloadTask(self, task):
        if self.channel.run():
            try:
                self.progBar['value'] = 100.*self.channel.getBytesDownloaded()/self.channel.getFileSize()
            except:
                pass
            return task.cont
        self.filesDownloaded += 1
        self.stopTrackingDownloadTime()
        self.progBar['value'] = 0
        self.nextFile()
        return task.done

    def sendMD5(self, fileName):
        dg = PyDatagram()
        dg.addUint16(CLIENT_MD5)
        dg.addString(fileName)
        dg.addString(self.currentMD5)
        self.cWriter.send(dg, self.Connection)

    def __handleServerMD5(self, dgi):
        servermd5 = dgi.getString()
        if servermd5 == self.currentMD5:
            self.nextFile()
        else:
            self.downloadFile()

    def exitUpdateFiles(self):
        self.title.pack_forget()
        del self.title
        self.progBar.pack_forget()
        del self.progBar
        self.infoLbl.pack_forget()
        del self.infoLbl

    def enterMenu(self):
        self.userNameEntryLbl = Label(self.tk, text = "Username:")
        self.passwordEntryLbl = Label(self.tk, text = "Password:")
        self.userNameEntryLbl.place(x = 10, y = 10)
        self.passwordEntryLbl.place(x = 10, y = 40)
        self.userNameEntry = Entry(self.tk, textvariable = self.loginUserName)
        self.passwordEntry = Entry(self.tk, textvariable = self.loginPassword, show = "*")
        self.userNameEntry.place(x = 80, y = 10)
        self.passwordEntry.place(x = 80, y = 40)
        self.loginBtn = Button(self.tk, text = "  Play  ", command = self.__handleLoginButton)
        self.loginBtn.place(x=210, y=25)
        self.crashBtn = Button(self.tk, text = "Game Crashes When It Opens", command = self.sendToHelpVideo)
        self.crashBtn.pack(side=BOTTOM)
        self.accBtn = Button(self.tk, text = "Create Account", command = self.__handleAccCreateButton)
        self.accBtn.pack(side=BOTTOM)#(x = 85, y = 67)

    def sendToHelpVideo(self):
        os.startfile(self.helpVideoLink)

    def __handleAccCreateButton(self):
        self.launcherFSM.request('accCreate')

    def exitMenu(self):
        self.userNameEntryLbl.place_forget()
        self.passwordEntryLbl.place_forget()
        self.userNameEntry.place_forget()
        self.passwordEntry.place_forget()
        self.loginBtn.place_forget()
        self.accBtn.pack_forget()
        self.crashBtn.pack_forget()
        del self.userNameEntryLbl
        del self.passwordEntryLbl
        del self.userNameEntry
        del self.passwordEntry
        del self.loginBtn
        del self.accBtn
        del self.crashBtn

    def enterConnect(self):
        self.connectingLbl = Label(self.tk, text = "Connecting...")
        self.connectingLbl.pack()
        self.tk.update()
        self.Connection = self.cMgr.openTCPClientConnection(self.Server_host, self.loginServer_port, self.timeout)
        self.noConnectionDialog = None
        if self.Connection:
            self.cReader.addConnection(self.Connection)
        if self.Connection:
            taskMgr.add(self.datagramPoll, "datagramPoll", -40)
            self.launcherFSM.request('validate')
        else:
            self.__handleNoConnection()

    def __handleNoConnection(self):
        self.noConnectionDialog = tkMessageBox.showwarning(parent = self.tk, title = "Error", message = "Could not connect to the servers.")
        sys.exit()

    def exitConnect(self):
        self.connectingLbl.pack_forget()
        del self.connectingLbl
        if self.noConnectionDialog:
            self.noConnectionDialog.destroy()
            del self.noConnectionDialog

    def __handleLoginButton(self):
        self.launcherFSM.request('updateFiles')

    def enterLogin(self):
        self.loggingInLbl = Label(self.tk, text = "Logging in...")
        self.loggingInLbl.pack()
        self._sendLoginCredidentials()

    def _sendLoginCredidentials(self):
        dg = PyDatagram()
        dg.addUint16(ACC_VALIDATE)
        dg.addString(self.loginUserName.get())
        dg.addString(self.loginPassword.get())
        # Send this to the account server which is self.Connection
        self.cWriter.send(dg, self.Connection)

    def __handleCredidentialResp(self, resp, dgi):
        if resp == ACC_VALID:
            self.__handleValidCredidentials(dgi)
        else:
            self.__handleInvalidCredidentials()

    def __handleValidCredidentials(self, dgi):
        self.gameServer = dgi.getString()
        self.gameVersion = dgi.getString()
        self.loginToken = dgi.getString()
        self.launcherFSM.request('play')

    def __handleInvalidCredidentials(self):
        self.invalidDialog = tkMessageBox.showwarning(parent = self.tk, message = "Username and/or password is incorrect.", title = "Error")
        del self.invalidDialog
        self.launcherFSM.request('menu')

    def exitLogin(self):
        self.loggingInLbl.pack_forget()
        del self.loggingInLbl

    def enterAccCreate(self):
        self.title = Label(self.tk, text = "Create an Account")
        self.title.pack()
        self.userNameEntryLbl = Label(self.tk, text = "Username:")
        self.passwordEntryLbl = Label(self.tk, text = "Password:")
        self.userNameEntryLbl.place(x = 10, y = 25)
        self.passwordEntryLbl.place(x = 10, y = 55)
        self.userNameEntry = Entry(self.tk, textvariable = self.loginUserName)
        self.passwordEntry = Entry(self.tk, textvariable = self.loginPassword, show = "*")
        self.userNameEntry.place(x = 80, y = 25)
        self.passwordEntry.place(x = 80, y = 55)
        self.doneBtn = Button(self.tk, text = "Done", command = self.__handleAccCreateDone)
        self.doneBtn.place(x=210, y=35)
        self.backBtn = Button(self.tk, text = "<<", command = self.__handleGoBackButton)
        self.backBtn.place(x=0, y=75)
        self.doneBtn.config(state=NORMAL)
        self.userNameEntry.config(state=NORMAL)
        self.passwordEntry.config(state=NORMAL)
        self.backBtn.config(state=NORMAL)

    def __handleGoBackButton(self):
        self.launcherFSM.request('menu')

    def __handleAccCreateDone(self):
        self.launcherFSM.request('submitAcc')

    def __handleInvalidEntries(self, state):
        self.invalidMsg = tkMessageBox.showwarning(
            parent = self.tk,
            message = "Your account name and password must be at least 5 characters long. " + \
                "You cannot have whitespace or blank entries. Your account name and password cannot be identical.",
            title = "Bad Entries"
        )
        self.launcherFSM.request(state)

    def enterSubmitAcc(self):
        self.infoLbl = Label(self.tk, text = "Submitting...")
        self.infoLbl.pack()
        if not self.validateEntries():
            self.__handleInvalidEntries('accCreate')
            return
        dg = PyDatagram()
        dg.addUint16(ACC_CREATE)
        dg.addString(self.loginUserName.get())
        dg.addString(self.loginPassword.get())
        self.cWriter.send(dg, self.Connection)

    def exitSubmitAcc(self):
        self.infoLbl.pack_forget()
        del self.infoLbl

    def validateEntries(self):
        if (
            self.loginUserName.get().isspace() or len(self.loginUserName.get()) < 5 or
            self.loginUserName.get().lower() == self.loginPassword.get().lower() or
            self.loginPassword.get().isspace() or len(self.loginPassword.get()) < 5
        ):
            return False
        return True

    def __handleAccCreateResp(self, msg):
        if msg == ACC_CREATED:
            self.launcherFSM.request('menu')
        if msg == ACC_EXISTS:
            self.__handleAccExists()

    def __handleAccExists(self):
        self.accExisitsDialog = tkMessageBox.showwarning(parent = self.tk, message = "That account name already exists.", title = "Account Exists")
        del self.accExisitsDialog
        self.launcherFSM.request('accCreate')

    def exitAccCreate(self):
        self.title.pack_forget()
        self.userNameEntry.place_forget()
        self.passwordEntry.place_forget()
        self.userNameEntryLbl.place_forget()
        self.passwordEntryLbl.place_forget()
        self.doneBtn.place_forget()
        self.backBtn.place_forget()
        del self.backBtn
        del self.title
        del self.userNameEntry
        del self.passwordEntry
        del self.userNameEntryLbl
        del self.passwordEntryLbl
        del self.doneBtn

    def enterPlay(self):
        self.playingLbl = Label(self.tk, text = "Launching game...")
        self.playingLbl.pack()
        self.cMgr.closeConnection(self.Connection)
        os.environ['ACCOUNT_NAME'] = self.loginUserName.get()
        os.environ['GAME_SERVER'] = self.gameServer
        os.environ['GAME_VERSION'] = self.gameVersion
        os.environ['LOGIN_TOKEN'] = self.loginToken
        os.system("start coginvasion.exe")
        self.launcherFSM.requestFinalState()
        sys.exit()

    def exitPlay(self):
        self.playingLbl.pack_forget()
        del self.playingLbl

    def handleDatagram(self, datagram):
        dgi = DatagramIterator(datagram)
        msgType = dgi.getUint16()
        if msgType == ACC_VALID or msgType == ACC_INVALID:
            self.__handleCredidentialResp(msgType, dgi)
        elif msgType == ACC_CREATED or msgType == ACC_EXISTS:
            self.__handleAccCreateResp(msgType)
        elif msgType == SERVER_MD5:
            self.__handleServerMD5(dgi)
        elif msgType in [LAUNCHER_GOOD, LAUNCHER_BAD]:
            self.__handleLauncherStatus(msgType)
        elif msgType == DL_LIST:
            self.__handleDLList(dgi)

    def __handleDLList(self, dgi):
        global baseLink
        global fileNames
        baseLink += dgi.getString()
        numFiles = dgi.getUint8()
        for i in range(numFiles):
            fileNames.append(dgi.getString())
        self.launcherFSM.request('menu')
        print fileNames

    def __handleLauncherStatus(self, msgType):
        if msgType == LAUNCHER_GOOD:
            self.launcherFSM.request('fetch')
        else:
            self.__handleBadLauncher()

    def datagramPoll(self, task):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                self.handleDatagram(datagram)
        return Task.cont


Launcher()
base.wxRun()

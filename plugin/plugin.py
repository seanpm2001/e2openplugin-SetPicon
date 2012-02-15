# for localized messages  	 
from . import _
#
#  Set Picon - Plugin E2
#
#  by ims (c) 2012
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

import os
from enigma import ePicLoad, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Components.config import ConfigSubsection, ConfigDirectory, ConfigSelection, getConfigListEntry, config, ConfigYesNo, ConfigLocations
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from os import system
import enigma
from Tools.Directories import resolveFilename, fileExists, pathExists
from Components.Button import Button
from enigma import eTimer
from Components.Renderer.Picon import initPiconPaths, searchPaths
from Screens.MessageBox import MessageBox

from Screens.ChoiceBox import ChoiceBox

SOURCE = "/picon/"
TARGET = "/picon/"

config.plugins.setpicon = ConfigSubsection()
config.plugins.setpicon.type = ConfigSelection(default = "0", choices = [("0",_("service reference")),("1",_("name"))])
config.plugins.setpicon.source = ConfigDirectory(SOURCE)
config.plugins.setpicon.target = ConfigDirectory(TARGET)
config.plugins.setpicon.allpicons = ConfigSelection(default = "0", choices = [("0",_("all picon's directories")),("1",_("input directory only"))])
config.plugins.setpicon.name_op = ConfigYesNo(default=False)
config.plugins.setpicon.filename = ConfigSelection(default = "0", choices = [("0",_("no")),("1",_("filename")),("2",_("full path"))])
config.plugins.setpicon.bookmarks = ConfigLocations(default=[SOURCE])
config.plugins.setpicon.extmenu = ConfigYesNo(default=False)

cfg = config.plugins.setpicon

SOURCE = cfg.source.value
TARGET = cfg.target.value

EXT = ".png"

class setPicon(Screen, HelpableScreen):
	skin = """
	<screen name="setPicon" position="center,center" size="560,290" backgroundColor="black" title="SetPicon">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="nowpicon" position="450,50" zPosition="2" size="100,60" alphatest="on"/>

		<widget name="name" position="10,50" zPosition="2" size="300,25" valign="center" halign="left" font="Regular;22" transparent="0" foregroundColor="white" />
		<widget name="current" position="340,50" zPosition="2" size="100,20" valign="top" halign="right" font="Regular;16" transparent="0" foregroundColor="white" />
		<widget name="reference" position="10,75" zPosition="2" size="430,20" valign="center" halign="left" font="Regular;18" transparent="0" foregroundColor="white" />
		<widget name="orbital" position="10,95" zPosition="2" size="100,20" valign="center" halign="left" font="Regular;18" transparent="0" foregroundColor="white" />

		<ePixmap pixmap="skin_default/div-h.png" position="10,120" zPosition="2" size="540,2" transparent="0" />

		<widget name="text" position="10,135" zPosition="2" size="540,25" valign="center" halign="left" font="Regular;18" transparent="0" foregroundColor="white" />

		<ePixmap pixmap="~/img/border.png" position="225,165" zPosition="1" size="110,70" transparent="0" />
		<widget name="picon2l" position="10,170" zPosition="2" size="100,60" alphatest="on"/>
		<widget name="picon1l" position="120,170" zPosition="2" size="100,60" alphatest="on"/>
		<widget name="picon"   position="230,170" zPosition="2" size="100,60" alphatest="on"/>
		<widget name="picon1p" position="340,170" zPosition="2" size="100,60" alphatest="on"/>
		<widget name="picon2p" position="450,170" zPosition="2" size="100,60" alphatest="on"/>

		<widget name="search" position="10,240" zPosition="2" size="200,22" valign="center" halign="left" font="Regular;18" transparent="0" foregroundColor="white" />
		<widget name="message" position="230,240" zPosition="2" size="100,22" valign="center" halign="center" font="Regular;18" transparent="0" foregroundColor="white" />
		<ePixmap pixmap="skin_default/div-h.png" position="10,264" zPosition="2" size="540,2" transparent="0" />
		<widget name="path" position="10,267" zPosition="2" size="540,22" valign="center" halign="center" font="Regular;18" transparent="0" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, plugin_path, services, bouquetname=None):
		self.skin = setPicon.skin
		self.skin_path = plugin_path
		self.EMPTY = plugin_path + "/img/empty.png"

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.services = services
		self.bouquetname = bouquetname
		self.setup_title = self.bouquetname

		self.lastPath = None

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.end, _("exit plugin")),
			"ok": (self.assignSelectedPicon,_("set and save selected picon")),
			})

		self["SetPiconActions"] = HelpableActionMap(self, "SetPiconActions",
			{
			"menu": (self.showMenu,_("menu")),
			"left": (self.previousPicon,_("go to previous picon")),
			"right": (self.nextPicon,_("go to next picon")),
			"up": (self.nextService,_("go to next service")),
			"down": (self.prevService,_("go to previous service")),
			"red": (self.end, _("exit plugin")),
			"green": (self.saveAssignedPicon,_("save service's picon")),
			"yellow": (self.searching,_("search picons or service")),
			"blue": (self.callConfig,_("options")),
			"first": (self.firstPicon,_("go to first picon")),
			"last": (self.lastPicon,_("go to last picon")),
			"1": (self.minusPiconX,_("go to -10 picons")),
			"4": (self.minusPiconC,_("go to -100 picons")),
			"7": (self.minusPiconM,_("go to -1000 picons")),
			"3": (self.plusPiconX,_("go to +10 picons")),
			"6": (self.plusPiconC,_("go to +100 picons")),
			"9": (self.plusPiconM,_("go to +1000 picons")),
			"8": (self.deleteSelectedPicon,_("delete selected picon")),
			"2": (self.getStoredPicons,_("refresh")),
			"service": (self.setSearchService,_("switch searching to service")),
			"picons": (self.setSearchPicon,_("switch searching to picons")),
			}, -2)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save current"))
		self["key_yellow"] = Button(_("Search"))
		self["key_blue"] = Button(_("Options"))

		self.initGraphic()

		self["current"] = Label()
		self["name"] = Label()
		self["reference"] = Label()
		self["orbital"] = Label()
		self["message"] = Label()
		self["text"] = Label(_("Please wait to finishing picon's list..."))
		self["path"] = Label()
		self["search"] = Label()

		self.maxPicons = 0
		self.idx = 0
		self.name = None
		self.refstr = None
		self.orbital = None

		self.ServicesList = []
		self.sidx = 0

		self.searchList = []
		self.search = False
		self.fidx = 0

		self.selection = 0

		self.search_picon = True
		self.blocked = False

		# fill ItemList with services from current bouquet
		for service in self.services: 
			self.ServicesList.append((service.getServiceName(), str(service)))
		self.lenServicesList = len(self.ServicesList)

		self.onLayoutFinish.append(self.delayStart)

	def delayStart(self):
		self.wait = eTimer()
		self.wait.timeout.get().append(self.runOnStart)
		self.wait.start(250, True)

	def runOnStart(self):
		self.setWindowTitle()
		self.setGraphic()
		self.getCurrentService()
		self["text"].setText(_("Reading picons..."))
		self.getStoredPicons()
		self["current"].setText(_("current:"))
		self.searchText()

	def showMenu(self):
		self.menu = []
		self.menu.append((_("Save %s bouquet's picons to %s") % (self.bouquetname, TARGET),0))
		self.menu.append((_("Copy all picons from %s to %s") % (SOURCE, TARGET),1))
		self.menu.append((_("Delete all picons in %s") % TARGET,2))
		if SOURCE != TARGET:
			self.menu.append((_("Delete all picons in %s") % SOURCE,3))

		self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_("Operations with picons"), list=self.menu, selection = self.selection)

	def menuCallback(self, choice):
		if choice is None:
			self.displayPicon()
			return
		selected = int(choice[1])
		if selected == 0:
			self.saveBouquetPicons()
		elif selected == 1:
			self.copyAllToOutput()
		elif selected == 2:
			self.deleteTarget()			
		elif selected == 3:
			self.deleteSource()
		else:
			return
		self.selection = selected

	def getStoredPicons(self):
		self.readPngFiles()
		self.firstPicon()

	def getCurrentService(self):
		from ServiceReference import ServiceReference
		if self.session.nav.getCurrentlyPlayingServiceReference():
			self.name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			self.refstr = self.session.nav.getCurrentlyPlayingServiceReference().toString()
			self.orbital =  self.getOrbitalPosition(self.refstr)
		self.displayServiceParams()
		self.setCurrentServiceIndex()

	def setCurrentServiceIndex(self):
		if self.ServicesList.count((self.name,self.refstr)):
			self.sidx = self.ServicesList.index((self.name,self.refstr))

	def displayServiceParams(self):
		self["name"].setText(self.name)
		self["reference"].setText(self.refstr)
		self["orbital"].setText(self.orbital)
		self.displayCurServicePicon()

	def displayCurServicePicon(self):
		path = self.getInternalPicon(self.ref2str(self.refstr))
		if fileExists(path) and not self.blocked:
			self.nowLoad.startDecode(path)
		else:
			self.nowLoad.startDecode(self.EMPTY)

	def assignSelectedPicon(self):
		if not len(self.picon) or self.blocked:
			print "[SetPicon] OK: blocked or no picons", len(self.picon), self.blocked
			return
		filename = self.ref2str(self.refstr)
		if cfg.type.value == "1":
			filename = self.name2str(self.name)
			if cfg.name_op.value:
				filename += "_" + self.getOrbitalPosition(self.refstr)
		path = SOURCE + self.picon[self.idx] + EXT
		if fileExists(path):
			print "[SetPicon] cp", path, TARGET + filename + EXT
			os.system("cp %s %s" % ( path, TARGET + filename + EXT ))
			self.displayCurServicePicon()
		else:
			print "[SetPicon] source does not exist", path
		print "[SetPicon] OK button"

	def saveAssignedPicon(self):
		if self.blocked:
			print "[SetPicon] blocked"
			return
		self.savePicon(self.ServicesList[self.sidx])
		self.displayPicon()
		self.search = False
		print "[SetPicon] GREEN button"

	def saveBouquetPicons(self):
		if SOURCE != TARGET or cfg.allpicons.value == "0":
			for idx in self.ServicesList:
				self.savePicon(idx, True)
			self.displayPicon()
			self.search = False
		else:
			self.session.openWithCallback(self.setSameDirectories, MessageBox, _("Input directory and output directory are same!"), MessageBox.TYPE_ERROR, timeout=5 )

	def setSameDirectories(self, answer):
		return

	def savePicon(self, item, bouquet=False):
		refstr = self.ref2str(item[1])
		if cfg.allpicons.value == "1":
			path = SOURCE + refstr + EXT
		else:
			path = self.getInternalPicon(refstr)
		filename = refstr
		if cfg.type.value == "1":
			filename = self.name2str(item[0])
			if cfg.name_op.value:
				filename += "_" + self.getOrbitalPosition(item[1])
		if fileExists(path):
			if not bouquet:
				print "[SetPicon] cp", path, TARGET + filename + EXT
			os.system("cp %s %s" % ( path, TARGET + filename + EXT ))
			if not self.picon.count(filename):
				self.picon.append(filename)
				self.maxPicons+=1
		else:
			print "[SetPicon] path does not exist:", path

	def setWindowTitle(self):
		self.setTitle(_("SetPicon") + "  -  " + self.bouquetname)

	def displayMsg(self, message):
		self["message"].setText(message)

	def displayText(self):
		if len(self.picon):
			text = _("Select picon and press OK to assign to current service:")
			if cfg.type.value != "0":
				text = _("Select picon and save it with OK to output directory:")
		else:
			text = _("In menu change input directory or save picons from bouquet.")
		self["text"].setText(text)

	def searchService(self):
		index = 0
		founded = False
		for item in self.ServicesList:
			(service, refstr, name, nameo, orbital ) = self.getStrings(item)
			if service == refstr or service == name or service == nameo:
				founded = True
				self.refstr = item[1]
				self.name = item[0]
				self.orbital = orbital
				break
			index += 1
		if founded:
			self.sidx = index
			self.displayServiceParams()
			self.blocked = False
		else:
			self.displayPath(_("Not found"))
			self.blocked = True
			self.serviceHide()

	def serviceHide(self):
		self["name"].setText(_("Service not found"))
		self["reference"].setText("")
		self["orbital"].setText("")
		self.displayCurServicePicon()

	def servicePiconRefresh(self):
		self.search = False
		self["key_yellow"].setText(_("Search"))
		if self.blocked:
			self.blocked = False
			self.displayPath("%s" % SOURCE + self.picon[self.idx] + EXT)
		self.displayServiceParams()

	def getStrings(self, item):
		name = self.name2str(item[0])
		orbital = self.getOrbitalPosition(item[1])
		return ( self.picon[self.idx], self.ref2str(item[1]), self.name2str(item[0]), name + "_" + orbital, orbital)

	def setSearchService(self):
		self.search_picon = False
		self.searchText()
		self.servicePiconRefresh()


	def setSearchPicon(self):
		self.search_picon = True
		self.searchText()
		self.servicePiconRefresh()

	def searchText(self):
		text = _("Search: picons")
		if not self.search_picon:
			text = _("Search: service")
		self["search"].setText(text)

	def readPngFiles(self):
		self.idx = 0
		filelist = FileList(SOURCE, matchingPattern="png")
		self.maxPicons = 0
		self.picon = []
		for x in filelist.getFileList():
			if (x[0][1] != True):
				self.picon.append(x[0][0][:-4])
				self.maxPicons += 1
		self.search = False
		self.blocked = False
		self.displayText()

	def searching(self):
		if self.search_picon:
			self.searchPicon()
		else:
			self.searchService()

	def searchPicon(self):
		if not len(self.picon):
			return
		if self.search:
			self.displayFoundedPicon()
		else:
			self.fidx = 0
			self.searchList = []

			item = self.ref2str(self.refstr)
			if self.picon.count(item):
				self.searchList.append(self.picon.index(item))
			item = self.name2str(self.name)
			if self.picon.count(item):
				self.searchList.append(self.picon.index(item))
			item += "_" + self.getOrbitalPosition(self.refstr)
			if self.picon.count(item):
				self.searchList.append(self.picon.index(item))

			if len(self.searchList):
				print "[SetPicon] found:", self.searchList
				self.search = True
				self.displayFoundedPicon()
			else:
				self["key_yellow"].setText(_("Search"))
				self.displayPath(_("Not found"))

	def displayFoundedPicon(self):
		text = _("Search")
		if len(self.searchList) != 1:
			text += " (%s/%s)" % (self.fidx+1, len(self.searchList))
		self["key_yellow"].setText(text)
		self.displayPath("%s" % self.picon[self.searchList[self.fidx]])
		self.gotoPicon(self.searchList[self.fidx], True)
		self.fidx += 1
		self.fidx %= len(self.searchList)

	def displayPath(self, text):
		if cfg.filename.value == "0":
			text = ""
		if cfg.filename.value == "1":
			text = text[text.rfind('/')+1:]
		self["path"].setText(text)

	def copyAllToOutput(self):
		if SOURCE != TARGET:
			os.system("cp %s %s" % ( SOURCE + "*" + EXT, TARGET ))
			#self.getStoredPicons()
		else:
			self.session.openWithCallback(self.setSameDirectories, MessageBox, _("Input directory and output directory are same!"), MessageBox.TYPE_ERROR, timeout=5 )

	def deleteTarget(self):
		self.rmPath = TARGET
		self.confirmDelete(TARGET)

	def deleteSource(self):
		self.rmPath = SOURCE
		self.confirmDelete(SOURCE)
		
	def confirmDelete(self, path):
		self.session.openWithCallback(self.deleteAllPicons, MessageBox, _("Are You sure delete all picons in %s ?") % path, MessageBox.TYPE_YESNO, default=False )

	def deleteAllPicons(self, answer=False):
		if answer is True:
			for filename in os.listdir(self.rmPath):
				if filename.endswith('.png'):
					try:
						filename = os.path.join(self.rmPath,filename)
						os.unlink(filename)
					except:
						print "Failed to unlink", filename
			self.getStoredPicons()
		del self.rmPath

	def nextPicon(self):
		self.gotoPicon(1)

	def previousPicon(self):
		self.gotoPicon(-1)

	def firstPicon(self):
		self.gotoPicon(0, True)
		
	def lastPicon(self):
		self.gotoPicon(self.maxPicons-1, True)

	def plusPiconX(self):
		self.gotoPicon(10)

	def plusPiconC(self):
		self.gotoPicon(100)

	def plusPiconM(self):
		self.gotoPicon(1000)

	def minusPiconX(self):
		self.gotoPicon(-10)

	def minusPiconC(self):
		self.gotoPicon(-100)

	def minusPiconM(self):
		self.gotoPicon(-1000)

	def gotoPicon(self, position, absolute=False):
		if len(self.picon):
			if absolute:
				self.idx = position
			else:
				self.idx += position
				self.idx %= self.maxPicons
		self.displayPicon()

	def displayPicon(self):
		if len(self.picon):
			path = SOURCE + self.picon[(self.idx-2) % self.maxPicons] + EXT
			if fileExists(path):
				self.piconLoad2l.startDecode(path)
			path = SOURCE + self.picon[(self.idx-1) % self.maxPicons] + EXT
			if fileExists(path):
				self.piconLoad1l.startDecode(path)
			path = SOURCE + self.picon[self.idx] + EXT
			if fileExists(path):
				self.piconLoad.startDecode(path)
				self.displayPath(path)
			path = SOURCE + self.picon[(self.idx+1) % self.maxPicons] + EXT
			if fileExists(path):
				self.piconLoad1p.startDecode(path)
			path = SOURCE + self.picon[(self.idx+2) %self.maxPicons] + EXT
			if fileExists(path):
				self.piconLoad2p.startDecode(path)
			self.displayMsg("%s/%s" % (self.idx+1, self.maxPicons))
			if self.blocked:
				self.servicePiconRefresh()
		else:
			if fileExists(self.EMPTY):
				self.piconLoad2l.startDecode(self.EMPTY)
				self.piconLoad1l.startDecode(self.EMPTY)
				self.piconLoad.startDecode(self.EMPTY)
				self.piconLoad1p.startDecode(self.EMPTY)
				self.piconLoad2p.startDecode(self.EMPTY)
				self["path"].setText("")
				self.displayMsg(_("No picons found!"))
				self.displayText()
				self.blocked = False

	def nextService(self):
		self.changeService(1)

	def prevService(self):
		self.changeService(-1)

	def changeService(self, num):
		self.sidx += num
		self.sidx %= self.lenServicesList
		self.name = self.ServicesList[self.sidx][0]
		self.refstr = self.ServicesList[self.sidx][1]
		self.orbital =  self.getOrbitalPosition(self.refstr)
		self.servicePiconRefresh()

	def getInternalPicon(self, serviceRef):
		if self.lastPath:
			pngname = self.lastPath + serviceRef + EXT
			if pathExists(pngname):
				return pngname
		global searchPaths
		for path in searchPaths:
			if pathExists(path):
				pngname = path + serviceRef + EXT
				if pathExists(pngname):
					self.lastPath = path
					return pngname
		return ""

	def ref2str(self, serviceRef):
		return '_'.join(serviceRef.split(':', 10)[:10])

	def name2str(self, serviceName):
		return serviceName.replace(' ','_').replace('/','__')

	def getOrbitalPosition(self, serviceRef):
		b = int("".join(serviceRef.split(':', 10)[6:7])[:-4],16)
		direction = 'E'
		if b > 1800:
			b = 3600 - b
			direction = 'W'
		return ("%d.%d%s") % (b // 10, b % 10, direction)

	def deleteSelectedPicon(self):
		if not len(self.picon):
			return
		self.removePath = SOURCE + self.picon[self.idx] + EXT
		self.session.openWithCallback(self.removePicon, MessageBox, _("Are You sure delete picon?\n%s") % self.removePath, MessageBox.TYPE_YESNO, default=False )

	def removePicon(self, answer):
		if answer is True:
			if fileExists(self.removePath):
				os.unlink(self.removePath)
			self.picon.pop(self.idx)
			self.maxPicons-=1
			self.search = False
			if self.maxPicons:
				self.idx %= self.maxPicons
			else:
				self.idx = 0
			self.displayPicon()
		del self.removePath			

	def end(self):
		self.close()

	def callConfig(self):
		self.lastdir = cfg.source.value
		self.session.openWithCallback(self.afterConfig, setPiconCfg)

	def afterConfig(self, data=None):
		self.displayText()
		if self.lastdir != cfg.source.value:
			self.getStoredPicons()
		else:
			self.displayPicon()

### for graphics
	def initGraphic(self):
		self["picon2l"] = Pixmap()
		self.piconLoad2l = enigma.ePicLoad()
		self.piconLoad2l.PictureData.get().append(self.showPicon2l)
		self["picon1l"] = Pixmap()
		self.piconLoad1l = enigma.ePicLoad()
		self.piconLoad1l.PictureData.get().append(self.showPicon1l)
		self["picon"] = Pixmap()
		self.piconLoad = enigma.ePicLoad()
		self.piconLoad.PictureData.get().append(self.showPicon)
		self["picon1p"] = Pixmap()
		self.piconLoad1p = enigma.ePicLoad()
		self.piconLoad1p.PictureData.get().append(self.showPicon1p)
		self["picon2p"] = Pixmap()
		self.piconLoad2p = enigma.ePicLoad()
		self.piconLoad2p.PictureData.get().append(self.showPicon2p)

		self["nowpicon"] = Pixmap()
		self.nowLoad = enigma.ePicLoad()
		self.nowLoad.PictureData.get().append(self.showNowPicon)

	def setGraphic(self):
		par = [self["picon2l"].instance.size().width(), self["picon2l"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.piconLoad2l.setPara(par)
		par = [self["picon1l"].instance.size().width(), self["picon1l"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.piconLoad1l.setPara(par)
		par = [self["picon"].instance.size().width(), self["picon"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.piconLoad.setPara(par)
		par = [self["picon1p"].instance.size().width(), self["picon1p"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.piconLoad1p.setPara(par)
		par = [self["picon2p"].instance.size().width(), self["picon2p"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.piconLoad2p.setPara(par)

		par = [self["nowpicon"].instance.size().width(), self["nowpicon"].instance.size().height(), 1, 1, False, 0, "#00000000"]
		self.nowLoad.setPara(par)

	def showPicon2l(self, picInfo=None):
		ptr = self.piconLoad2l.getData()
		if ptr != None:
			self["picon2l"].instance.setPixmap(ptr.__deref__())
			self["picon2l"].show()
	def showPicon1l(self, picInfo=None):
		ptr = self.piconLoad1l.getData()
		if ptr != None:
			self["picon1l"].instance.setPixmap(ptr.__deref__())
			self["picon1l"].show()
	def showPicon(self, picInfo=None):
		ptr = self.piconLoad.getData()
		if ptr != None:
			self["picon"].instance.setPixmap(ptr.__deref__())
			self["picon"].show()
	def showPicon1p(self, picInfo=None):
		ptr = self.piconLoad1p.getData()
		if ptr != None:
			self["picon1p"].instance.setPixmap(ptr.__deref__())
			self["picon1p"].show()
	def showPicon2p(self, picInfo=None):
		ptr = self.piconLoad2p.getData()
		if ptr != None:
			self["picon2p"].instance.setPixmap(ptr.__deref__())
			self["picon2p"].show()

	def showNowPicon(self, picInfo=None):
		ptr = self.nowLoad.getData()
		if ptr != None:
			self["nowpicon"].instance.setPixmap(ptr.__deref__())
			self["nowpicon"].show()
###

class setPiconCfg(Screen, ConfigListScreen):
	skin = """
	<screen name="setPiconCfg" position="center,center" size="560,380" title="SetPicon Setup"  backgroundColor="black">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="config" position="10,40" size="540,300" zPosition="1" transparent="0" backgroundColor="black" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/div-h.png" position="0,355" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,361" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="right" position="495,358" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="statusbar" position="10,359" size="460,20" font="Regular;18" backgroundColor="black" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = setPiconCfg.skin
		self.setup_title = _("SetPicon Setup")
			
		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Swap Dirs"))
		self["key_blue"] = Label(_("Same Dirs"))

		self["statusbar"] = Label("ims (c) 2012, v0.25")
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.save,
			"ok": self.ok,
			"red": self.exit,
			"cancel": self.exit,
			"yellow": self.swapDirs,
			"blue": self.bothAsInputDir
		}, -2)

		self.onChangedEntry = []
		self.refreshMenu()
		ConfigListScreen.__init__(self, self.setPiconCfglist, session, on_change = self.changedEntry)

		self.onShown.append(self.setWindowTitle)

	def refreshMenu(self):
		self.source_entry = getConfigListEntry(_("Input directory"), cfg.source)
		self.target_entry = getConfigListEntry(_("Output directory"), cfg.target)

		self.setPiconCfglist = []
		self.setPiconCfglist.append(getConfigListEntry(_("Save picon as"), cfg.type))
		if cfg.type.value == "1":
			self.setPiconCfglist.extend((
				getConfigListEntry(_("Save name with orbital position"), cfg.name_op),
			))
		self.setPiconCfglist.append(self.source_entry)
		self.setPiconCfglist.append(self.target_entry)
		self.setPiconCfglist.append(getConfigListEntry(_("Saving current picons from"), cfg.allpicons))
		self.setPiconCfglist.append(getConfigListEntry(_("Display picon's name"), cfg.filename))
		self.setPiconCfglist.append(getConfigListEntry(_("SetPicon in E-menu"), cfg.extmenu))

	# for summary:
	def changedEntry(self):
		self.refresh()
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
	###
	def setWindowTitle(self):
		self.setTitle(_("SetPicon Setup"))

	def refresh(self):
		self.refreshMenu()
		self["config"].setList(self.setPiconCfglist)

	def ok(self):
		from Screens.LocationBox import LocationBox
		currentry = self["config"].getCurrent()
		if currentry == self.source_entry:
			txt = _("Input directory of Picons")
			inhibitDirs = ["/autofs", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/tmp", "/usr"]
			self.session.openWithCallback(self.sourceDirSelected, LocationBox, text=txt, currDir=cfg.source.value,
							bookmarks=cfg.bookmarks, autoAdd=False, editDir=True,
							inhibitDirs=inhibitDirs)
		elif currentry == self.target_entry:
			txt = _("Output directory for created Picons")
			inhibitDirs = ["/autofs", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/tmp", "/usr"]
			self.session.openWithCallback(self.targetDirSelected, LocationBox, text=txt, currDir=cfg.target.value,
							bookmarks=cfg.bookmarks, autoAdd=False, editDir=True,
							inhibitDirs=inhibitDirs, minFree=10 ) # in MB

	def sourceDirSelected(self, res):
		if res is not None:
			cfg.source.value = res

	def targetDirSelected(self, res):
		if res is not None:
			cfg.target.value = res

	def swapDirs(self):
		tmp = cfg.target.value
		cfg.target.value = cfg.source.value
		cfg.source.value = tmp
		self["config"].invalidate(self["config"].list[self.setPiconCfglist.index(self.source_entry)])
		self["config"].invalidate(self["config"].list[self.setPiconCfglist.index(self.target_entry)])

	def bothAsInputDir(self):
		self.session.openWithCallback(self.sameDirs, MessageBox, _("Do you want set both directory as:\n %s") % cfg.source.value , MessageBox.TYPE_YESNO, default=False )

	def sameDirs(self, answer=False):
		if answer:
			cfg.target.value = cfg.source.value
			self["config"].invalidate(self["config"].list[self.setPiconCfglist.index(self.target_entry)])

	def save(self):
		global SOURCE
		SOURCE = cfg.source.value
		global TARGET
		TARGET = cfg.target.value
		self.keySave()

	def exit(self):
		self.keyCancel()

from enigma import eServiceCenter, eServiceReference
from ServiceReference import ServiceReference

def getBouquetServices(bouquet):
	services = [ ]
	Servicelist = eServiceCenter.getInstance().list(bouquet)
	if not Servicelist is None:
		while True:
			service = Servicelist.getNext()
			if not service.valid(): #check if end of list
				break
			if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker): #ignore non playable services
				continue
			services.append(ServiceReference(service))
	return services

def main(session, servicelist=None, **kwargs):
	global Servicelist
	Servicelist = servicelist
	global epg_bouquet
	epg_bouquet = Servicelist and Servicelist.getRoot()
	if epg_bouquet is not None:
		services = getBouquetServices(epg_bouquet)
		session.open(setPicon, plugin_path, services, ServiceReference(epg_bouquet).getServiceName())

def Plugins(path,**kwargs):
	global plugin_path
    	plugin_path = path
	name="SetPicon"
	descr=_("set picon to service")
	list = [ PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EVENTINFO, needsRestart = False, fnc=main),]
	if cfg.extmenu.value:
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart = False, fnc=main))
	return list

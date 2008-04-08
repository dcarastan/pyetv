#
#  main.py
#  FrontPython
#
#  Copyright 2008 Jon A Christopher. All rights reserved.
#

import os, time
import objc
from PyFR import *

from PyFR.BackRow import *

import PyFR.Appliance 
import PyFR.WaitController
import PyFR.MenuController
import PyFR.Utilities
import PyFR.Debugging
import PyFR.OptionDialog

from etv import ETV
import string

######################################################################
# local logging
import Foundation
def log(s):
    #Foundation.NSLog( "%s: %s" % ("PyeTV", str(s) ) )
    pass
#end
######################################################################


class RecordingsMenu(PyFR.MenuController.Menu):
    def GetRightText(self):
        return str(len(self.items) - 1)

################################################################################

class ETVWaitController(PyFR.WaitController.WaitController, PyFR.Utilities.ControllerUtilities):
    def initWithStartup_exitCond_(self, startup=None, exitCond=None):
        log("initWithStartup_exitCond_")
        self.tickCount=0
        self.startup=startup
        self.exitCond=exitCond
        return PyFR.WaitController.WaitController.initWithText_(self, "Launching EyeTV")

    def PyFR_start(self):
        log("PyFR_start called_")
        self.tickCount = 0
        if self.startup is not None:
            self.call_startup = True
        else:
            self.call_startup = False
        self.launchApp( '/Applications/EyeTV.app')

    def AppShouldExit(self):
        self.tickCount = self.tickCount+1

#         a=PyFR.Utilities.ControllerUtilities();
#         if self.tickCount < 100:
#             a.disableObjCCapture() # call this to to enable flushing cache!
#             #a.enableObjCCapture()

#         # re-enable logging after ~20 minutes so we can catch the exit of FrontRow
#         if self.tickCount >= 4780:
#             a.disableObjCCapture() # call this to to enable flushing cache!
#             a.enableObjCCapture()

        # tune these parameters
        wait_before_calling_startup = 1
        wait_before_exit_ticks=20

        # possibly call startup code
        if self.call_startup and self.tickCount >= wait_before_calling_startup:
            try:
                self.startup()
                self.call_startup = False
            except:
                log("App::startup failed with tickCount=%d" % self.tickCount)
                pass

        # give EyeTV a chance to stabilize, and then disable FrontRow's annoying auto-exit feature
        # so that we can get back here no matter how long the recording is!
        if self.tickCount ==wait_before_exit_ticks: 
            AutoQuitManager = objc.lookUpClass("FRAutoQuitManager")
            AutoQuitManager.sharedManager().setAutoQuitEnabled_(False)

        # there's no startup function, so just wait for stabilization first
        if self.exitCond is not None and self.tickCount > wait_before_exit_ticks: 
            log("calling exitCond(), tickCount=%d" % self.tickCount)
            return not self.exitCond()
        return False


    def AboutToHideFR(self):
        pass

    def FRWasShown(self):
        log("**************** FRWasShown *****************");
        self.stack().popController()

################################################################################

class ETVMenuController(PyFR.MenuController.MenuController):
    
    def GetRecordingMetadata(self, controller, rec):
        mdc=BRMetadataControl.alloc().init()
        mdc.setTitle_(rec.GetTitle())
        mdc.setSummary_(rec.GetDescription())

        labels=[
            "Episode",
            "Channel",
            "Duration",
            "Start time"
            ]
        data=[
            rec.GetEpisode(),
            rec.GetChannelStr(),
            rec.GetDuration(True),
            str(rec.GetStartTime())
            ]

        mdc.setMetadata_withLabels_(data,labels)
        return mdc

    def GetRecordingsDict(self):
        log("in getrecordingsdict")
        series_dict={}
        rec=ETV.GetRecordings()
        log("Got %d recordings" % len(rec))
        for r in rec:
            title=r.GetTitle()
            series_dict[title]=[]

        for r in rec:
            title=r.GetTitle()
            series_dict[title].append(r)
        return series_dict

    def MakeRecordingsMenu(self):
        root=RecordingsMenu("EyeTV Recordings", [])
        log("recordings menu now has %d items" % len(root.items))
        series=self.GetRecordingsDict()
        k=series.keys()
        k.sort()
        for s in k:
            submenu=RecordingsMenu(s, [])
            root.AddItem(submenu)
            for ep in series[s]:
                epstr=ep.GetEpisodeAndDate()
                item=PyFR.MenuController.MenuItem(epstr, self.RecordingOptionsDialog, ep, self.GetRecordingMetadata)
                submenu.AddItem(item)
            item=PyFR.MenuController.MenuItem("Delete all",self.ConfirmDeleteRecordingDialog, series[s])
            submenu.AddItem(item)
        return root


    def PlayChannel(self, controller, chan):
        newCon=ETVWaitController.alloc().initWithStartup_exitCond_(chan.Play,ETV.IsPlaying)
        return controller.stack().pushController_(newCon)

    def MakeChannelsMenu(self):
        chan=ETV.GetChannels()
        root=PyFR.MenuController.Menu("Channels",[])
        for c in chan:
            chstr=c.GetName()
            item=PyFR.MenuController.MenuItem(chstr, self.PlayChannel, c)
            root.AddItem(item)
        return root

    def DeleteEntry(self, rec, doPop):
        title=rec.GetTitle()
        episode=rec.GetEpisodeAndDate()

        # find title in menus
        for series_menu in self.recordings_menu.items:
            if series_menu.page_title==title:
                log("Found series_menu menu, %d items" % len(series_menu.items))
                for ep_menu_item in series_menu.items:
                    if ep_menu_item.title==episode:
                        if len(series_menu.items)==2:
                            log("removing series menu")
                            self.recordings_menu.items.remove(series_menu)
                            if doPop:
                                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(self.recordings_menu)
                                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
                        else:
                            log("removing episode from series menu")
                            series_menu.items.remove(ep_menu_item)
                            if doPop:
                                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(series_menu)
                                self.stack().replaceControllersAboveLabel_withController_("EyeTV Recordings",con)
                        ETV.DeleteRecording(rec)
                        return False # don't pop

    def ConfirmDeleteRecordingDialogHandler(self, controller, idx, item):
        log("ConfirmDeleteRecordingDialogHandler")
        rec=item.data
        if idx==0:
            if isinstance(rec,list):
                for r in rec:
                    self.DeleteEntry(r, False)
                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(self.recordings_menu)
                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
            else:
                self.DeleteEntry(rec, True)            
            return False
        return True
            
    def RecordingOptionsDialogHandler(self, controller, idx, item):
        log("RecordingOptionsDialogHandler")
        rec=item.data
        if idx==0 or idx==1:
            ETV.SetCurrentRecording(rec,idx==1)
            newCon=ETVWaitController.alloc().initWithStartup_exitCond_(ETV.PlayCurrentRecording,ETV.IsPlaying)
            return controller.stack().pushController_(newCon)
        if idx==2:
            log("deletion request")
            return self.ConfirmDeleteRecordingDialog(controller, rec)
        if idx==3:
            log("comskip toggle request")
            if self.AppRunning("ComSkipper"):
                os.system("killall ComSkipper &")
            else:
                os.system("/Library/Application\ Support/ETVComskip/ComSkipper.app/Contents/MacOS/ComSkipper &")
            time.sleep(0.5)
        if idx==4:
            log("MarkCommercials request")
            log("/Library/Application\ Support/ETVComskip/MarkCommercials.app/Contents/MacOS/MarkCommercials --log %s &" % rec.rec.unique_ID.get())
            os.system("/Library/Application\ Support/ETVComskip/MarkCommercials.app/Contents/MacOS/MarkCommercials --log %s &" % rec.rec.unique_ID.get())

        if idx==3 or idx==4:
            dlg=self.GetRecordingOptionsDialog(rec)
            controller.stack().swapController_(dlg)

        # if we return true, we'll pop the controller and back up past the option dialog
        return False

    def ConfirmDeleteRecordingDialog(self, controller, rec):
        log("in confirm delete recordings dialog")
        options=[ PyFR.OptionDialog.OptionItem("Yes",rec), 
                  PyFR.OptionDialog.OptionItem("No",rec) ]
        if isinstance(rec,list):
            title="Are you sure you want to delete %d recordings from %s?" % (len(rec),rec[0].GetTitle())
            dlg=PyFR.OptionDialog.OptionDialog.alloc().initWithTitle_Items_Handler_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
        else:
            title="Are you sure you want to delete '" + rec.GetTitle()+ ": " + rec.GetEpisode() + " " + str(rec.GetStartTime()) + "' ?"
            dlg=PyFR.OptionDialog.OptionDialog.alloc().initWithTitle_Items_Handler_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
            
        return controller.stack().pushController_(dlg)

    def AppRunning(self, appname):
        process = os.popen("ps x | grep %s | grep -v grep" % appname).read()
        if process:
            return True
        return False

    def GetRecordingOptionsDialog(self, rec):
        pos=rec.GetPlaybackPosition(True)
        end=rec.GetDuration(True)

        options=[ PyFR.OptionDialog.OptionItem("Play @ %s / %s" % (pos,end), rec),
                  PyFR.OptionDialog.OptionItem("Restart", rec),
                  PyFR.OptionDialog.OptionItem("Delete", rec)
                  #PyFR.OptionDialog.OptionItem("Comskip On/Off", rec),
                  #PyFR.OptionDialog.OptionItem("Scan file", rec)
                  ]
        if os.path.exists("/Library/Application Support/ETVComskip/ComSkipper.app") and \
                os.path.exists("/Library/Application Support/ETVComskip/MarkCommercials.app"):
            if self.AppRunning("ComSkipper"):
                comskip_state="ComSkipper                      [On]"
            else:
                comskip_state="ComSkipper                      [Off]"

            options.append(PyFR.OptionDialog.OptionItem(comskip_state, rec))
            if rec.GetMarkerCount()==0:
                if self.AppRunning("MarkCommercials"):
                    options.append(PyFR.OptionDialog.OptionItem("Mark Commercials    [Running]", rec))
                else:
                    options.append(PyFR.OptionDialog.OptionItem("Mark Commercials", rec))

        title=rec.GetTitle()+ ": " + rec.GetEpisode() + " " + str(rec.GetStartTime())
        dlg=PyFR.OptionDialog.OptionDialog.alloc().initWithTitle_Items_Handler_("Recording options", options, self.RecordingOptionsDialogHandler)
        dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
        return dlg

    def RecordingOptionsDialog(self, controller, rec):
        log("in recording options dialog")
        dlg=self.GetRecordingOptionsDialog(rec)
        return controller.stack().pushController_(dlg)


    def StartETV(self, controller, arg):
        log("in StartETV")
        newCon=ETVWaitController.alloc().initWithStartup_exitCond_(ETV.ShowMenu,None)
        return controller.stack().pushController_(newCon)

    def StartETVGuide(self, controller, arg):
        log("in StartETVGuide")
        newCon=ETVWaitController.alloc().initWithStartup_exitCond_(ETV.ShowGuide,ETV.IsFullScreen)
        return controller.stack().pushController_(newCon)
        

    def init(self):
        log("Initing recordings")
        self.recordings_menu=self.MakeRecordingsMenu()
        log("Initing menus")
        self.menu=PyFR.MenuController.Menu("EyeTV",
                  [
                self.recordings_menu,
                self.MakeChannelsMenu(),
                PyFR.MenuController.MenuItem("Enter EyeTV",   self.StartETV),
                PyFR.MenuController.MenuItem("Program guide", self.StartETVGuide)
                #            ,PyFR.MenuController.MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,PyFR.MenuController.MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,PyFR.MenuController.MenuItem("Option dialog",   testOptionDialogTest, "Text test")
                #            ,PyFR.MenuController.MenuItem("Text test",   TestText_MenuHandler, "Text test")
                ])

        ac=PyFR.MenuController.MenuController.initWithMenu_(self, self.menu)
        log("Done initing menus")
        return ac
        


class RUIPythonAppliance( PyFR.Appliance.Appliance ):

    def getController(self):
        self.log("**************************************************")
        self.log("Appliance controller starting, Enabling logger")
        #a=PyFR.Utilities.ControllerUtilities();
        #a.enableObjCCapture() # call this to to enable flushing cache!
        #self.log("enabled")

        ret=ETVMenuController.alloc().init()
        return ret






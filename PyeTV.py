# PyeTV
# 
# Copyright 2008 Jon A Christopher. All rights reserved.

import os, time, string
import objc

# PyFR imports
from PyFR.BackRow import *
import PyFR.AppLauncherController
import PyFR.Appliance 
import PyFR.MenuController
import PyFR.Utilities
import PyFR.Debugging
import PyFR.OptionDialog

# PyeTV imports
from PyeTVMetaData import *
from PyeTVWaitController import *
from etv import ETV

import Logger
def log(s):
    #Logger.log(s)
    pass

SERIES_LABEL="Recordings by series"
ALL_RECORDINGS_LABEL="All recordings"

class RecordingsMenu(PyFR.MenuController.Menu):
    def GetRightText(self):
        return str(len(self.items) - 1)

################################################################################
# Work around EyeTV bug:
#
# When EyeTV is showing Live TV, and "menu" is pressed to return to front row
# it (unfortunately) "remembers" that live tv was playing and tries to re-open
# a live tv window after Front Row exits, even though we've closed the window.
#
# Therefore, we have to install this "Cleaner" thread which waits until after
# Front Row is no longer visible to close all windows.
#
# When we exit Front Row, we don't want EyeTV windows open.

import threading
CleanerShouldHideWindow=False
class Cleaner ( threading.Thread ):
    def run ( self ):
        global CleanerShouldHideWindow

        self.shouldHide=False
        fr = BRAppManager.sharedApplication().delegate()

        while(1):
            time.sleep(0.5)
            if CleanerShouldHideWindow and not fr.uiVisible():
                # by user requests; let's hide all EyeTV windows before we leave the appliance
                ETV.HideWindows()
                CleanerShouldHideWindow=False


################################################################################

class ETVMenuController(PyFR.MenuController.MenuController):
    def AppRunning(self, appname):
        process = os.popen("ps xc | grep %s" % appname).read()
        if process:
            return True
        return False

    def GetRecordingMetadata(self, controller, rec):
        return PyeTVPreviewMetadataController.alloc().initWithRecording_(rec)

    def GetRecordingMetadataFromTuple(self, controller, rec):
        return PyeTVPreviewMetadataController.alloc().initWithRecording_(rec[0])

    def GetSeriesMetadata(self, controller, series):
        log("requested preview for series %s" % (series))
        if series not in self.series_dict.keys():
            return None
        return PyeTVPreviewMetadataController.alloc().initWithSeriesEpisode_(self.series_dict[series][0])

    def GetChannelMetadata(self, controller, channel):
        log("requested preview for channel %s" % str(channel))
        return PyeTVPreviewMetadataController.alloc().initWithChannel_(channel)

    def MakeSeriesMenu(self):
        root=RecordingsMenu(SERIES_LABEL, [],  self.GetSeriesMetadata)
        log("recordings menu now has %d items" % len(root.items))
        self.series_dict=series=ETV.GetRecordingsDict()
        k=series.keys()
        k.sort()
        for s in k:
            submenu=RecordingsMenu(s, [], self.GetSeriesMetadata)
            root.AddItem(submenu)

            # sort by date
            series_episodes={}
            for ep in series[s]:
                series_episodes[ep.GetDate()]=ep
            date_keys=series_episodes.keys();
            date_keys.sort()

            for epdate in date_keys:
                ep=series_episodes[epdate]
                epstr=ep.GetEpisodeAndDate()
                item=PyFR.MenuController.MenuItem(epstr, self.RecordingOptionsMenu, ep, self.GetRecordingMetadata, True)
                submenu.AddItem(item)
            item=PyFR.MenuController.MenuItem("Delete all",self.ConfirmDeleteRecordingDialog, series[s], None, True)
            submenu.AddItem(item)
        return root

    def MakeChannelsMenu(self):
        chan=ETV.GetChannels()
        root=PyFR.MenuController.Menu("Channels",[])
        for c in chan:
            chstr=c.GetName()
            item=PyFR.MenuController.MenuItem(chstr, self.PlayChannel, c, self.GetChannelMetadata, False)
            root.AddItem(item)
        return root

    def ConfirmDeleteRecordingDialog(self, controller, rec):
        log("in confirm delete recordings dialog")
        options=[ PyFR.OptionDialog.OptionItem("Yes",rec), 
                  PyFR.OptionDialog.OptionItem("No",rec) ]
        if isinstance(rec,list):
            title="Are you sure you want to delete %d recordings from %s?" % (len(rec),rec[0].GetTitle())
            dlg=PyFR.OptionDialog.OptionDialog.alloc().initWithTitle_Items_Handler_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
        else:
            title="Are you sure you want to delete '" + rec.GetTitle()+ ": " + rec.GetEpisode() + " " + rec.GetStartTime() + "' ?"
            dlg=PyFR.OptionDialog.OptionDialog.alloc().initWithTitle_Items_Handler_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
            
        return controller.stack().pushController_(dlg)

    def ConfirmDeleteRecordingDialogHandler(self, controller, idx, item):
        log("ConfirmDeleteRecordingDialogHandler")
        rec=item.data
        if idx!=0:
            return True

        if isinstance(rec,list):
            currentSeries=rec[0].GetTitle()
            for r in rec:
                ETV.DeleteRecording(r)
        else:
            currentSeries=rec.GetTitle()
            ETV.DeleteRecording(rec)
                
        # now, re-build menu tree
        self.updateMainMenu()

        # if the series still exists, back up that far
        for item in self.series_menu.items:
            if item.page_title==currentSeries:
                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(item)
                controller.stack().replaceControllersAboveLabel_withController_(SERIES_LABEL,con)
                return False

        # series is gone, back up to EyeTV menu
        con=PyFR.MenuController.MenuController.alloc().initWithMenu_(self.series_menu)
        controller.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
        return False

    def RecordingOptionsMenuHandler(self, controller, data):
        log("RecordingOptionsMenuHandler, controller is %s" % str(controller))
        log("Stack is %s, controller stack is %s" % (self.stack(),controller.stack()))
        try:
            rec=data[0]
            idx=data[1]
        except:
            return

        log("Got idx: %s rec %s" % (repr(idx), repr(rec)))
        if idx==0 or idx==1:
            ETV.SetCurrentRecording(rec,idx==1)
            newCon=PyeTVWaitController.alloc().initWithStartup_(ETV.PlayCurrentRecording)
            return controller.stack().pushController_(newCon)
        if idx==2:
            return self.ConfirmDeleteRecordingDialog(controller, rec)
        if idx==3:
            if self.AppRunning("ComSkipper"):
                os.system("/usr/bin/killall ComSkipper &")
                self.CurrentOptionsMenu.ds.menu.items[3].layer.setTitle_("ComSkipper                     [Off]") # deep magic
            else:
                os.system("/Library/Application\ Support/ETVComskip/ComSkipper.app/Contents/MacOS/ComSkipper &")
                self.CurrentOptionsMenu.ds.menu.items[3].layer.setTitle_("ComSkipper                      [On]") # deep magic
            time.sleep(0.5)

        if idx==4:
            log("/Library/Application\ Support/ETVComskip/MarkCommercials.app/Contents/MacOS/MarkCommercials --log %s &" % rec.rec.unique_ID.get())
            os.system("/Library/Application\ Support/ETVComskip/MarkCommercials.app/Contents/MacOS/MarkCommercials --log %s &" % rec.rec.unique_ID.get())

        # if we return true, we'll pop the controller and back up past the option dialog
        return False

    def GetRecordingOptionsMenu(self, rec):
        items= [
            PyFR.MenuController.MenuItem("Play",   self.RecordingOptionsMenuHandler, (rec, 0), self.GetRecordingMetadataFromTuple),
            PyFR.MenuController.MenuItem("Restart", self.RecordingOptionsMenuHandler, (rec, 1), self.GetRecordingMetadataFromTuple),
            PyFR.MenuController.MenuItem("Delete",   self.RecordingOptionsMenuHandler, (rec, 2), self.GetRecordingMetadataFromTuple)
            ]
        
        if self.HasETVComskip:
            comskip_state="ComSkipper                      [Off]"
            if self.AppRunning("ComSkipper"):
                comskip_state="ComSkipper                      [On]"
            items.append(PyFR.MenuController.MenuItem(comskip_state,   self.RecordingOptionsMenuHandler, (rec, 3), self.GetRecordingMetadataFromTuple))
            if rec.GetMarkerCount()==0:
                mc_state="Mark Commercials"
                if self.AppRunning("MarkCommercials"):
                    mc_state="Mark Commercials    [Running]"
                items.append(PyFR.MenuController.MenuItem(mc_state, self.RecordingOptionsMenuHandler, (rec, 4), self.GetRecordingMetadataFromTuple))

        menu=PyFR.MenuController.Menu(rec.GetTitle(), items)
        dlg=PyFR.MenuController.MenuController.alloc().initWithMenu_(menu)
        self.CurrentOptionsMenu = dlg
        return dlg

    def RecordingOptionsMenu(self, controller, rec):
        log("in recording options dialog")
        dlg=self.GetRecordingOptionsMenu(rec)
        return controller.stack().pushController_(dlg)

    # WaitController startup callback
    def PlayChannel(self, controller, chan):
        newCon=PyeTVWaitController.alloc().initWithStartup_(chan.Play)
        return controller.stack().pushController_(newCon)

    # WaitController startup callback
    def StartETVGuide(self, controller, arg):
        log("in StartETVGuide")
        newCon=PyeTVWaitController.alloc().initWithStartup_(ETV.ShowGuide)
        return controller.stack().pushController_(newCon)

    # re-create series menu tree and sub it into the main menu
    def updateMainMenu(self):
        self.series_menu=self.MakeSeriesMenu()
        self.MainMenu.items[0]=self.series_menu

    def init(self):
        self.HasETVComskip = os.path.exists("/Library/Application Support/ETVComskip/ComSkipper.app") and \
                             os.path.exists("/Library/Application Support/ETVComskip/MarkCommercials.app")

        log("Initing recordings")
        self.series_menu=self.MakeSeriesMenu()
        log("Initing menus")
        self.MainMenu=PyFR.MenuController.Menu("EyeTV",
                  [
                self.series_menu,
                self.MakeChannelsMenu(),
                PyFR.MenuController.MenuItem("Program guide", self.StartETVGuide),
                ])

        # chain to parent's ctor
        ac=PyFR.MenuController.MenuController.initWithMenu_(self,self.MainMenu)

        log("Done initing menus")
        return ac

    def willBePushed(self):
        global CleanerShouldHideWindow
        CleanerShouldHideWindow =  False
        
    def willBePopped(self):
        global CleanerShouldHideWindow
        log("ETVMenuController willBePopped")
        CleanerShouldHideWindow = True 
        return BRMediaMenuController.willBePopped(self)


class RUIPythonAppliance( PyFR.Appliance.Appliance ):

    def getController(self):
        self.log("************ PyeTV Starting **********************************")

        Cleaner().start() # init clean up thread 

        # Optionally enable ObjC logging now
        #a=PyFR.Utilities.ControllerUtilities();
        #a.enableObjCCapture() # call this to to enable flushing cache!

        # Or, turn on logging to /tmp/msgSends while /tmp/FRLOG exists
        #PyFR.Debugging.EnableObjcLogger()

        ret=ETVMenuController.alloc().init()
        return ret




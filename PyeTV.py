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
from Logger import log

SERIES_LABEL="Recordings by series"
ALL_RECORDINGS_LABEL="All recordings"

class RecordingsMenu(PyFR.MenuController.Menu):
    def GetRightText(self):
        return str(len(self.items) - 1)


################################################################################

class ETVMenuController(PyFR.MenuController.MenuController):

    def GetRecordingMetadata(self, controller, rec):
        return PyeTVPreviewMetadataController.alloc().initWithRecording_(rec)

    def GetRecordingMetadataFromTuple(self, controller, rec):
        return PyeTVPreviewMetadataController.alloc().initWithRecording_(rec[0])

    def GetSeriesMetadata(self, controller, series):
        log("requested preview for series %s" % (series))
        if series not in self.series_dict.keys():
            return None
        # FIXME: create this function and get metadata populator to get screenshots for series, too
        return PyeTVPreviewMetadataController.alloc().initWithSeriesEpisode_(self.series_dict[series][0])

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

    def MakeAllRecordingsMenu(self):
        root=RecordingsMenu(ALL_RECORDINGS_LABEL, [],  self.GetSeriesMetadata)
        log("recordings menu now has %d items" % len(root.items))
        
        rec_dict={}
        rec=ETV.GetRecordings()
        log("Got %d recordings" % len(rec))
        for r in rec:
            rec_dict[r.GetDate()]=r
        date_keys=rec_dict.keys();
        date_keys.sort(reverse=True)

        for epdate in date_keys:
            ep=rec_dict[epdate]
            epstr=ep.GetStartTime() + " " + ep.GetTitle()[:22]
            item=PyFR.MenuController.MenuItem(epstr, self.RecordingOptionsMenu, ep, self.GetRecordingMetadata, True)
            root.AddItem(item)
        return root


    def PlayChannel(self, controller, chan):
        newCon=PyeTVWaitController.alloc().initWithStartup_exitCond_(chan.Play,ETV.IsPlaying)
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
        for series_menu in self.series_menu.items:
            if series_menu.page_title==title:
                log("Found series_menu menu, %d items" % len(series_menu.items))
                for ep_menu_item in series_menu.items:
                    if ep_menu_item.title==episode:
                        if len(series_menu.items)==2:
                            log("removing series menu")
                            self.series_menu.items.remove(series_menu)
                            if doPop:
                                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(self.series_menu)
                                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
                        else:
                            log("removing episode from series menu")
                            series_menu.items.remove(ep_menu_item)
                            if doPop:
                                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(series_menu)
                                self.stack().replaceControllersAboveLabel_withController_(SERIES_LABEL,con)
                        ETV.DeleteRecording(rec)
                        return False # don't pop

    def ConfirmDeleteRecordingDialogHandler(self, controller, idx, item):
        log("ConfirmDeleteRecordingDialogHandler")
        rec=item.data
        if idx==0:
            if isinstance(rec,list):
                for r in rec:
                    self.DeleteEntry(r, False)
                con=PyFR.MenuController.MenuController.alloc().initWithMenu_(self.series_menu)
                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
            else:
                self.DeleteEntry(rec, True)            
            return False
        return True
            
    def RecordingOptionsMenuHandler(self, controller, data):
        log("RecordingOptionsMenuHandler, controller is %s" % str(controller))
        try:
            rec=data[0]
            idx=data[1]
        except:
            return

        log("Got idx: %s rec %s" % (repr(idx), repr(rec)))
        if idx==0 or idx==1:
            ETV.SetCurrentRecording(rec,idx==1)
            newCon=PyeTVWaitController.alloc().initWithStartup_exitCond_(ETV.PlayCurrentRecording,ETV.IsPlaying)
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

    def AppRunning(self, appname):
        process = os.popen("ps x | grep %s | grep -v grep" % appname).read()
        if process:
            return True
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
        dlg=PyFR.MenuController.MenuController.initWithMenu_(self, menu)
        self.CurrentOptionsMenu = dlg
        return dlg

    def RecordingOptionsMenu(self, controller, rec):
        log("in recording options dialog")
        dlg=self.GetRecordingOptionsMenu(rec)
        return controller.stack().pushController_(dlg)

    def StartETVGuide(self, controller, arg):
        log("in StartETVGuide")
        #newCon=PyeTVWaitController.alloc().initWithStartup_exitCond_(ETV.ShowGuide,ETV.IsFullScreen)
        newCon=PyeTVWaitController.alloc().initWithStartup_exitCond_(ETV.ShowGuide,None)
        return controller.stack().pushController_(newCon)

    def init(self):
        log("Initing recordings")
        self.series_menu=self.MakeSeriesMenu()
        #self.recordings_menu=self.MakeAllRecordingsMenu()
        log("Initing menus")
        self.menu=PyFR.MenuController.Menu("EyeTV",
                  [
                self.series_menu,
                #self.recordings_menu,
                self.MakeChannelsMenu(),
                PyFR.MenuController.MenuItem("Program guide", self.StartETVGuide),
                #            ,PyFR.MenuController.MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,PyFR.MenuController.MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,PyFR.MenuController.MenuItem("Option dialog",   testOptionDialogTest, "Text test")
                #            ,PyFR.MenuController.MenuItem("Text test",   TestText_MenuHandler, "Text test")
                ])

        ac=PyFR.MenuController.MenuController.initWithMenu_(self, self.menu)
        self.HasETVComskip = os.path.exists("/Library/Application Support/ETVComskip/ComSkipper.app") and \
            os.path.exists("/Library/Application Support/ETVComskip/MarkCommercials.app")
        log("Done initing menus")
        return ac
        
    def willBePopped(self):
        # by user requests; let's hide all EyeTV windows before we leave the appliance
        ETV.HideWindows()
        return BRMediaMenuController.willBePopped(self)



class RUIPythonAppliance( PyFR.Appliance.Appliance ):

    def getController(self):
        self.log("************ PyeTV Starting **********************************")

        # Optionally enable ObjC logging now
        #a=PyFR.Utilities.ControllerUtilities();
        #a.enableObjCCapture() # call this to to enable flushing cache!

        # Or, turn on logging to /tmp/msgSends while /tmp/FRLOG exists
        #PyFR.Debugging.EnableObjcLogger()

        ret=ETVMenuController.alloc().init()
        return ret






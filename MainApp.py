#
#  main.py
#  FrontPython
#
#  Created by garion on 12/15/07.
#  Copyright __MyCompanyName__ 2007. All rights reserved.
#

from  PyFR import *
from  PyFR import *
from  PyFR import *
from  PyFR import *
from  PyFR import *

from PyFR.BackRow import *
from etv import ETV
import string

######################################################################
# local logging
import Foundation
def log(s):
    Foundation.NSLog( "%s: %s" % ("PyeTV", str(s) ) )
#end
######################################################################


#is the fullscreen menu up in EyeTV
def MenuGone():
    log("In MenuGone()")
    return not ETV.IsFullScreen()

def InstallExitHandler(controller):
    time.sleep(1.0) # allow time for fs menu to stabilize before installing exit handler
    controller.setExitConditionTest(MenuGone)


COMSKIP_IS_ON="ON"
def HasSkipFile(arg):
    return "Not Found"


################################################################################

class RecordingsMenu(Menu):
    def GetRightText(self):
        return str(len(self.items) - 1)

################################################################################

class ETVWaitController(WaitController, ControllerUtilities):
    def initWithStartup_exitCond_(self, startup=None, exitCond=None):
        log("initWithStartup_exitCond_")
        self.tickCount=0
        self.startup=startup
        self.exitCond=exitCond
        return WaitController.initWithText_(self, "Launching EyeTV")

    def PyFR_start(self):
        self.launchApp( '/Applications/EyeTV.app')

    def AppShouldExit(self):
        self.tickCount = self.tickCount+1

        wait_ticks=16

        # tune these parameters
        if self.tickCount < wait_ticks:
            log("App not stabilized")
            return False  # not stabilized yet
        elif self.tickCount == wait_ticks and self.startup is not None:
            log("App::startup")
            self.startup()
            return False
        elif self.tickCount < wait_ticks*2:
            log("App::post-startup")
            return False
        elif self.exitCond is not None:
            return not self.exitCond()
        return False

    def AboutToHideFR(self):
        pass

    def FRWasShown(self):
        pass




################################################################################

class ETVMenuController(MenuController):
    
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
                item=MenuItem(epstr, self.RecordingOptionsDialog, ep, self.GetRecordingMetadata)
                submenu.AddItem(item)
            item=MenuItem("Delete all",self.ConfirmDeleteRecordingDialog, series[s])
            submenu.AddItem(item)
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
                                con=MenuController.alloc().initWithMenu_(self.recordings_menu)
                                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
                        else:
                            log("removing episode from series menu")
                            series_menu.items.remove(ep_menu_item)
                            if doPop:
                                con=MenuController.alloc().initWithMenu_(series_menu)
                                self.stack().replaceControllersAboveLabel_withController_("EyeTV Recordings",con)
                        #ETV.DeleteRecording(rec)
                        return False # don't pop

    def ConfirmDeleteRecordingDialogHandler(self, controller, idx, rec):
        log("ConfirmDeleteRecordingDialogHandler")

        if idx==0:
            if isinstance(rec,list):
                for r in rec:
                    self.DeleteEntry(r, False)
                con=MenuController.alloc().initWithMenu_(self.recordings_menu)
                self.stack().replaceControllersAboveLabel_withController_("EyeTV",con)
            else:
                self.DeleteEntry(rec, True)            
            return False
        return True
            
    def RecordingOptionsDialogHandler(self, controller, idx, rec):
        log("RecordingOptionsDialogHandler")
        if idx==0 or idx==1:
            ETV.SetCurrentRecording(rec,idx==1)
            newCon=ETVWaitController.alloc().initWithStartup_exitCond_(ETV.PlayCurrentRecording,ETV.IsPlaying)
            return controller.stack().pushController_(newCon)
        if idx==2:
            log("deletion request")
            return self.ConfirmDeleteRecordingDialog(controller, rec)
        if idx==3:
            log("comskip toggle request")
        if idx==4:
            log("skipfile scan request")

        # if we return true, we'll pop the controller and back up past the option dialog
        return False

    def ConfirmDeleteRecordingDialog(self, controller, rec):
        log("in confirm delete recordings dialog")
        options=[ "Yes", "No" ]
        if isinstance(rec,list):
            title="Are you sure you want to delete %d recordings from %s?" % (len(rec),rec[0].GetTitle())
            dlg=OptionDialog.alloc().initWithTitle_Items_Handler_UserData_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler, rec)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
        else:
            title="Are you sure you want to delete '" + rec.GetTitle()+ ": " + rec.GetEpisode() + " " + str(rec.GetStartTime()) + "' ?"
            dlg=OptionDialog.alloc().initWithTitle_Items_Handler_UserData_("Delete recording(s):", options, self.ConfirmDeleteRecordingDialogHandler, rec)
            dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
            
        return controller.stack().pushController_(dlg)
        
    def RecordingOptionsDialog(self, controller, rec):
        log("in recording options dialog")
        pos=rec.GetPlaybackPosition(True)
        end=rec.GetDuration(True)
        options=[ "Play @ %s / %s" % (pos,end),
                  "Restart",
                  "Delete",
                  "coming soon: Comskip [%s]" % COMSKIP_IS_ON,
                  "coming soon: SkipFile [%s]" % HasSkipFile(rec) ]  

        title=rec.GetTitle()+ ": " + rec.GetEpisode() + " " + str(rec.GetStartTime())
        dlg=OptionDialog.alloc().initWithTitle_Items_Handler_UserData_("Recording options", options, self.RecordingOptionsDialogHandler, rec)
        dlg.setPrimaryInfoText_withAttributes_(title,BRThemeInfo.sharedTheme().promptTextAttributes())
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
        self.menu=Menu("EyeTV",
                  [
                self.recordings_menu,
                MenuItem("Enter EyeTV",   self.StartETV),
                MenuItem("Program guide", self.StartETVGuide)
                #            ,MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,MenuItem("Comskip off",   ShowGuide_MenuHandler)
                #            ,MenuItem("Option dialog",   testOptionDialogTest, "Text test")
                #            ,MenuItem("Text test",   TestText_MenuHandler, "Text test")
                ])

        ac=MenuController.initWithMenu_(self, self.menu)
        log("Done initing menus")
        return ac
        


class RUIPythonAppliance( Appliance ):

    def getController(self):
        self.log("**************************************************")
        self.log("Appliance controller starting, Enabling logger")
        self.a=EnableObjcLogger()
        #self.log("enabled")

        ret=ETVMenuController.alloc().init()
        return ret





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
        self.textController.setTitle_("") # don't show "Launching EyeTV" when we come back

    def AppShouldExit(self):
        self.tickCount = self.tickCount+1

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
        try:
            # sometimes this doesn't work!
            self.stack().popController()
        except:
            pass

################################################################################

class PyeTVMediaAsset(BRSimpleMediaAsset):
    def initWithRecording_(self, rec):
        log("PyeTVMediaAsset inited for rec %s" % rec.GetTitle());
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.rec=rec
        self.firstTime=True
        self.IsSeries=False
        return self

    def initWithSeriesEpisode_(self, rec):
        log("PyeTVMediaAsset inited for rec %s" % rec.GetTitle());
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.rec=rec
        self.firstTime=True
        self.IsSeries=True
        return self

    def coverArt(self):
        log("PyeTVMediaAsset::coverArt")
        return BRImage.imageWithPath_(self.rec.GetPreviewImagePath())

    # the first time this is called, it's apparently being asked if it conforms to a BRMediaAsset protocol.  The next time, a collection.
    def conformsToProtocol_(self, protocol):
         log("PyeTVMediaAsset::conformsToProtocol: %s" % repr(protocol))
         if self.firstTime:
             self.firstTime=False
             return True
         return False

class PyeTVMetadataPopulator(NSObject):
    def init(self):
        NSObject.init(self);
        return self

    def populateLayer_fromAsset_(self, layer, asset):
        log("We want to do magic stuff here for layer %s and asset %s" % (repr(layer), repr(asset)))
        if asset.IsSeries:
            return
        layer.setTitle_(asset.rec.GetTitle())
        layer.setSummary_(asset.rec.GetDescription())
        labels=[
            "Episode",
            "Channel",
            "Duration",
            "Start time"
            ]
        data=[
            asset.rec.GetEpisode(),
            asset.rec.GetChannelStr(),
            asset.rec.GetDuration(True),
            asset.rec.GetStartTime()
            ]
        layer.setMetadata_withLabels_(data,labels)
        return

    def axMetadataFromAsset_(self, asset):
        log("called axMetadataFromAsset %s" % repr(asset))
        return None

# custom metadata populator factory which will return a populator which understands EyeTV recordings
class PyeTVMetadataPopulatorFactory(BRSingleton):
    __Instance = None

    def init(self):
        __Instance=self
        self.pop=PyeTVMetadataPopulator.alloc().init()
        return BRSingleton.init(self)

    # Note: this isn't really a good singleton implementation, but it's good enough for our purposes here
    @classmethod
    def singleton(self):
        return self.__Instance

    def populatorForAsset_(self, asset):
        return self.pop


class PyeTVPreviewMetadataController(BRMetadataPreviewController):
    def initWithRecording_(self, rec):
        BRMetadataPreviewController.init(self)
        asset=PyeTVMediaAsset.alloc().initWithRecording_(rec)
        self.setAsset_(asset)
        self.setShowsMetadataImmediately_(True) # could comment this out for a bigger look at the screenshot, but the md is more important
        return self

    def initWithSeriesEpisode_(self, rec):
        BRMetadataPreviewController.init(self)
        asset=PyeTVMediaAsset.alloc().initWithSeriesEpisode_(rec)
        self.setAsset_(asset)
        #self.setShowsMetadataImmediately_(True) 
        return self

    def _updateMetadataLayer(self):
        # create temporary populator factory and replace standard one ---
        # I don't know how to get the standard populator to properly identify the asset,
        # and even if I did, one of the pre-defined assets probably wouldn't populate with the fields I want!

        # and yes, this is a horrible abuse of setSingleton_.
        log("PyeTVPreviewMetadataLayerController::_updateMetadataLayer")
        oldPopFactory=BRMetadataPopulatorFactory.sharedInstance()
        BRMetadataPopulatorFactory.setSingleton_(PyeTVMetadataPopulatorFactory.alloc().init())
        BRMetadataPreviewController._updateMetadataLayer(self)
        BRMetadataPopulatorFactory.setSingleton_(oldPopFactory)


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


    def GetRecordingsDict(self):
        log("in getrecordingsdict")
        self.series_dict={}
        rec=ETV.GetRecordings()
        log("Got %d recordings" % len(rec))
        for r in rec:
            title=r.GetTitle()
            self.series_dict[title]=[]

        for r in rec:
            title=r.GetTitle()
            self.series_dict[title].append(r)
        return self.series_dict

    def MakeRecordingsMenu(self):
        root=RecordingsMenu("EyeTV Recordings", [],  self.GetSeriesMetadata)
        log("recordings menu now has %d items" % len(root.items))
        series=self.GetRecordingsDict()
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
            newCon=ETVWaitController.alloc().initWithStartup_exitCond_(ETV.PlayCurrentRecording,ETV.IsPlaying)
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
        self.HasETVComskip = os.path.exists("/Library/Application Support/ETVComskip/ComSkipper.app") and \
            os.path.exists("/Library/Application Support/ETVComskip/MarkCommercials.app")
        log("Done initing menus")
        return ac
        


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






import objc
import Foundation
import AppKit
from appscript import *
import time
import PyFR as PFR

######################################################################
# local logging
import Foundation
def log(s):
    Foundation.NSLog( "%s: %s" % ("PyeTV", str(s) ) )
#end
######################################################################


class ETVRecording(PFR.ControllerUtilities):

    # comment this out for debugging
    def log(self,foo):
        return

    def __init__(self,rec):
        self.rec=rec

    def GetTitle(self):
        self.log("GetTitle called")
        ret=self.rec.title.get()
        self.log("log done")
        return ret

    def GetEpisode(self):
        self.log("GetEpisode called")
        ret = self.rec.episode.get()
        self.log("GetEpisode done")
        return ret

    def GetStartTime(self):
        self.log("GetStartTime called")
        ret = self.rec.start_time.get()
        self.log("GetStartTime done")
        return ret

    def GetEpisodeAndDate(self):
        return self.GetEpisode() + "" + str(self.GetStartTime())

    def ToStr(self,sec):
        self.log("ToStr called")
        shour = int(sec)/3600 # integer division
        smin = (sec - shour*3600)/60
        ret = "%d:%02d" % (shour, smin)
        self.log("ToStr done")
        return ret

    def GetPlaybackPosition(self, asString=False):
        self.log("GetPlaybackPosition called")
        ret=self.rec.playback_position.get()
        if not asString:
            ret = ret
            return ret
        ret = self.ToStr(ret)
        self.log("GetPlaybackPosition done")
        return ret

    def GetDuration(self, asString=False):
        self.log("GetDuration called")
        ret=self.rec.actual_duration.get()
        if not asString:
            ret = ret
            return ret
        ret = self.ToStr(ret)
        self.log("GetDuration done")
        return ret

    def GetDescription(self):
        self.log("GetDescription called")
        ret = self.rec.description.get()
        self.log("GetDescription done")
        return ret

    def GetChannelStr(self):
        self.log("GetChannelStr called")
        ret = str(self.rec.channel_number.get())  + " " + self.rec.station_name.get()
        self.log("GetChannelStr done")
        return ret


class EyeTV(PFR.ControllerUtilities):
    # comment this out for debugging
    def log(self,foo):
        return

    def GetRecordings(self):
        self.log("GetRecordings called")
        for i in range(1,10):  
            recs=app("EyeTV").recordings.get()
            if len(recs)>0:
                break
            time.sleep(1)
        retval=[]
        for r in recs:
            retval.append(ETVRecording(r))
        self.log("GetRecordings done")
        return retval

    def IsPlaying(self):
        self.log("IsPlaying called")
        ret=app("EyeTV").playing.get()
        self.log("IsPlaying done")
        return ret

    def IsFullScreen(self):
        self.log("IsFullScreen called")
        ret=app("EyeTV").full_screen_menu.get()
        self.log("IsFullScreen done")
        return ret

    def IsFullScreenOrPlaying(self):
        return self.IsFullScreen() or self.IsPlaying()

    def EnterFullScreen(self):
        self.log("EnterFullScreen called")
        app("EyeTV").enter_full_screen()
        self.log("EnterFullScreen done")
        
    def ShowMenu(self):
        self.log("ShowMenu called")
        etvGUI = app('System Events').processes['EyeTV']
        etvGUI.frontmost(True)
        mref = etvGUI.menu_bars[1].menus
        mref['View'].menu_items['Open Menu'].click()
        self.EnterFullScreen()
        self.log("ShowMenu done")

    def ShowGuide(self):
        self.log("ShowGuide called")
        self.ShowMenu()
        time.sleep(1) # give it time to happen
        app("System Events").keystroke("g",using=k.command_down)
        self.log("ShowGuide done")

    def SetCurrentRecording(self, rec, fromBeginning):
        self.rec=rec
        self.fromBeginning=fromBeginning

    def HideWindows(self):
        #app("EyeTV").controller_window.hide()
        #app("EyeTV").programs_window.hide()
        #wins=app("EyeTV").player_windows.get()
        #for w in wins:
        #    w.hide()
        pass

    def DeleteRecording(self):
        app("EyeTV").delete(recording=self.rec.rec)

    def PlayCurrentRecording(self):
        self.HideWindows()
        self.log("PlayRecording called")
        app("EyeTV").play(self.rec.rec)
        if self.fromBeginning:
            self.JumpTo(0)
        self.EnterFullScreen()
        self.log("PlayRecording done")

    def JumpTo(self,position):
        self.log("JumpTo called")
        app("EyeTV").jump(to=position)
        self.log("JumpTo done")

    def ShowProgramGuide(self):
        self.log("ShowProgramGuide called")
        app("System Events").keystroke("g",using=k.command_down)
        self.log("ShowProgramGuide done")


ETV=EyeTV()

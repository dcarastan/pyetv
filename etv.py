import objc
import Foundation
import AppKit
from appscript import *
import time

import PyFR.Utilities

######################################################################
# local logging
import Foundation
def log(s):
    Foundation.NSLog( "%s: %s" % ("PyeTV", str(s) ) )
    pass
######################################################################

ETV_CURRENT_RECORDING=None


class ETVChannel(PyFR.Utilities.ControllerUtilities):
    def __init__(self,chan):
        self.chan=chan

    def GetName(self):
        return str(self.chan.channel_number.get()) + " - " + self.chan.name.get()

    def Play(self):
        #app("EyeTV").player_windows.close()
        log("Trying2 to play channel number %d" % self.chan.channel_number.get())
        try:
            app("EyeTV").channel_change(channel_number = self.chan.channel_number.get())
        except:
            # recording? channnel is busy & can't be changed
            pass
        log("channel changed. playing")
        app("EyeTV").play()
        log("played. fs")
        app("EyeTV").enter_full_screen()
        # sometimes it doesn't play.  tell it again, just in case
        time.sleep(0.5)
        log("repeat")
        try:
            app("EyeTV").channel_change(channel_number = self.chan.channel_number.get())
        except:
            # recording? channnel is busy & can't be changed
            pass
        app("EyeTV").play()


class ETVRecording(PyFR.Utilities.ControllerUtilities):

    # comment this out for debugging
    def log(self,foo):
        #log(foo)
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

    # must be a HFS filename (e.g. ":tmp:screenshot.jpg"), not posix (/tmp/screenshot.jpg)
    def TakeScreenshot(self, fname):
        try:
            app("EyeTV").screenshot.set(fname)
            return True
        except:
            return False

    def GetPreviewImagePath(self):
        imgpath=""
        try:
            if self == ETV_CURRENT_RECORDING:
                # try screenshot first
                fname=":tmp:screenshot.jpg"
                app("EyeTV").screenshot.set(fname)
                return "/tmp/screenshot.jpg"
            else:
                loc=self.rec.location.get()
                f=loc.file.path
                f=f[:-6]+"tiff"
                if len(f)>0:
                    imgpath=f
        except:
            pass
        return imgpath

    def GetStartTime(self):
        ret = self.rec.start_time.get()
        return ret.strftime("%b %d %I:%M%p")

    def GetDate(self):
        return self.rec.start_time.get()

    def GetEpisodeAndDate(self):
        return self.GetStartTime() + " " + self.GetEpisode() 

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

    def GetMarkerCount(self):
        self.log("GetMarkerCount called")
        return len(self.rec.markers.get())




class EyeTV(PyFR.Utilities.ControllerUtilities):
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

    def GetChannels(self):
        self.log("GetChannels called")
        for i in range(1,10):  
            chan=app("EyeTV").channels.get()
            if len(chan)>0:
                break
            time.sleep(1)
        retval=[]
        for c in chan:
            if c.enabled.get():
                retval.append(ETVChannel(c))
        self.log("GetChannels done")
        return retval

    def IsPlaying(self):
        self.log("IsPlaying called")
        try:
            ret=app("EyeTV").playing.get()
        except:
            return false
        self.log("IsPlaying done")
        return ret

    def IsPaused(self):
        return not self.IsPlaying()

    def NotShowingMenu(self):
        self.log("NotShowingMenu called")
        ret=app("EyeTV").full_screen_menu.get()
        return not ret

    def ShowingMenu(self):
        self.log("ShowingMenu called")
        ret=app("EyeTV").full_screen_menu.get()
        return ret

    def EnterFullScreen(self):
        self.log("EnterFullScreen called")
        app("EyeTV").enter_full_screen()
        self.log("EnterFullScreen done")

    def HideMenu(self):
        app("EyeTV").full_screen_menu.set(False)
        app("EyeTV").stop()  # pause/stop any playback
        
        
    def ShowMenu(self):
        self.log("ShowMenu called")
        app("EyeTV").full_screen_menu.set(True)
        app("EyeTV").enter_full_screen(True)
        self.log("ShowMenu done")

    def ShowGuide(self):
        self.log("ShowGuide called")
        self.ShowMenu()
        time.sleep(2) # give it time to happen
        app("System Events").keystroke("g",using=k.command_down)
        self.log("ShowGuide done")

    def GetCurrentRecording(self):
        return self.rec

    def SetCurrentRecording(self, rec, fromBeginning):
        global ETV_CURRENT_RECORDING
        self.rec=rec
        ETV_CURRENT_RECORDING=self.rec
        self.fromBeginning=fromBeginning

    def HideWindows(self):
        app("EyeTV").controller_window.hide()
        app("EyeTV").programs_window.hide()
        wins=app("EyeTV").player_windows.get()
        for w in wins:
            w.close()

    def DeleteRecording(self,rec):
        app("EyeTV").stop()
        app("EyeTV").player_windows.close()
        app("EyeTV").delete(rec.rec)

    def PlayCurrentRecording(self):
        self.log("PlayRecording called to play recording %s%s" % (self.rec.GetTitle(), self.rec.GetEpisodeAndDate()))
        #self.HideWindows()
        time.sleep(0.5)
        app("EyeTV").play(self.rec.rec)
        app("EyeTV").play() # necessary if recording is paused
        if self.fromBeginning:
            self.JumpTo(0)
        app("EyeTV").enter_full_screen()

        # sometimes it doesn't play.  tell it again, just in case
        time.sleep(0.5)
        app("EyeTV").play(self.rec.rec)
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

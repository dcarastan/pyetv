import objc
import Foundation
import AppKit
from appscript import *
import time

import PyFR.Utilities

#for debugging
#from Logger import log
def log(s):
    pass

ETV_CURRENT_RECORDING=None

class ETVChannel(PyFR.Utilities.ControllerUtilities):
    def __init__(self,chan):
        self.chan=chan

    def GetName(self):
        return str(self.chan.channel_number.get()) + " - " + self.chan.name.get()

    def Play(self):
        app("EyeTV").player_windows.close()
        app("EyeTV").window.close()
        log("Trying2 to play channel number %d" % self.chan.channel_number.get())
        try:
            app("EyeTV").channel_change(channel_number = self.chan.channel_number.get())
        except:
            # recording? channnel is busy & can't be changed
            pass
        app("EyeTV").enter_full_screen()


class ETVRecording(PyFR.Utilities.ControllerUtilities):
    def __init__(self,rec):
        self.rec=rec

    def GetTitle(self):
        log("GetTitle called")
        try:
            ret=self.rec.title.get()
            return ret
        except:
            return ""

    def GetEpisode(self):
        log("GetEpisode called")
        try:
            ret = self.rec.episode.get()
        except:
            return ""
        log("GetEpisode done")
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
        try:
            ret = self.rec.start_time.get()
            return ret.strftime("%b %d %I:%M%p")
        except:
            return ""

    def GetDate(self):
        try:
            return self.rec.start_time.get()
        except:
            return ""

    def GetEpisodeAndDate(self):
        try:
            return self.GetStartTime() + " " + self.GetEpisode() 
        except:
            return ""

    def ToStr(self,sec):
        log("ToStr called")
        shour = int(sec)/3600 # integer division
        smin = (sec - shour*3600)/60
        ret = "%d:%02d" % (shour, smin)
        log("ToStr done")
        return ret

    def GetPlaybackPosition(self, asString=False):
        log("GetPlaybackPosition called")
        try:
            ret=self.rec.playback_position.get()
        except:
            return ""
        if not asString:
            ret = ret
            return ret
        ret = self.ToStr(ret)
        log("GetPlaybackPosition done")
        return ret

    def GetDuration(self, asString=False):
        log("GetDuration called")
        try:
            ret=self.rec.actual_duration.get()
        except:
            return ""
        if not asString:
            ret = ret
            return ret
        ret = self.ToStr(ret)
        log("GetDuration done")
        return ret

    def GetDescription(self):
        log("GetDescription called")
        try:
            ret = self.rec.description.get()
        except:
            return ""
        log("GetDescription done")
        return ret

    def GetChannelStr(self):
        log("GetChannelStr called")
        try:
            ret = str(self.rec.channel_number.get())  + " " + self.rec.station_name.get()
        except:
            return ""
        log("GetChannelStr done")
        return ret

    def GetMarkerCount(self):
        log("GetMarkerCount called")
        try:
            return len(self.rec.markers.get())
        except:
            return 0


class EyeTV(PyFR.Utilities.ControllerUtilities):
    def GetRecordings(self):
        log("GetRecordings called")
        for i in range(1,10):  
            recs=app("EyeTV").recordings.get()
            if len(recs)>0:
                break
            time.sleep(1)
        retval=[]
        for r in recs:
            retval.append(ETVRecording(r))
        log("GetRecordings done")
        return retval

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

    def GetChannels(self):
        log("GetChannels called")
        for i in range(1,10):  
            chan=app("EyeTV").channels.get()
            if len(chan)>0:
                break
            time.sleep(1)
        retval=[]
        for c in chan:
            if c.enabled.get():
                retval.append(ETVChannel(c))
        log("GetChannels done")
        return retval

    def IsPlaying(self):
        log("IsPlaying called")
        try:
            ret=app("EyeTV").playing.get()
        except:
            return false
        log("IsPlaying done")
        return ret

    def IsPaused(self):
        return not self.IsPlaying()

    def NotShowingMenu(self):
        log("NotShowingMenu called")
        ret=app("EyeTV").full_screen_menu.get()
        return not ret

    def ShowingMenu(self):
        log("ShowingMenu called")
        ret=app("EyeTV").full_screen_menu.get()
        return ret

    def EnterFullScreen(self):
        log("EnterFullScreen called")
        app("EyeTV").enter_full_screen()
        log("EnterFullScreen done")

    def HideMenu(self):
        app("EyeTV").full_screen_menu.set(False)
        app("EyeTV").stop()  # pause/stop any playback
        
        
    def ShowMenu(self):
        log("ShowMenu called")
        app("EyeTV").full_screen_menu.set(True)
        app("EyeTV").enter_full_screen(True)
        log("ShowMenu done")

    def IsFullScreen(self):
        log("IsFullScreen called")
        ret=app("EyeTV").full_screen_menu.get()
        log("IsFullScreen done")
        return ret

    def ShowGuide(self):
        log("ShowGuide called")
        self.ShowMenu()
        time.sleep(2) # give it time to happen
        app("System Events").keystroke("g",using=k.command_down)
        log("ShowGuide done")

    def GetCurrentRecording(self):
        return self.rec

    def SetCurrentRecording(self, rec, fromBeginning):
        global ETV_CURRENT_RECORDING
        self.rec=rec
        ETV_CURRENT_RECORDING=self.rec
        self.fromBeginning=fromBeginning

    def HideWindows(self):
        log("ETV: in HideWindows")
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
        log("PlayRecording called to play recording %s%s" % (self.rec.GetTitle(), self.rec.GetEpisodeAndDate()))
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
        log("PlayRecording done")

    def JumpTo(self,position):
        log("JumpTo called")
        app("EyeTV").jump(to=position)
        log("JumpTo done")

    def ShowProgramGuide(self):
        log("ShowProgramGuide called")
        app("System Events").keystroke("g",using=k.command_down)
        log("ShowProgramGuide done")


    def UpdateScreenShot(self):
        try:
            app("EyeTV").screenshot.set(":tmp:screenshot.jpg")
        except:
            pass

ETV=EyeTV()

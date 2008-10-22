import objc
from PyFR import *

import PyFR.WaitController
import PyFR.Utilities
from PyFR.BackRow import *

from etv import ETV
import Logger
def log(s):
    #Logger.log(s)
    pass

class PyeTVWaitController(PyFR.WaitController.WaitController, PyFR.Utilities.ControllerUtilities):
    """
    A Front Row controller which 

     1) launches an external app (EyeTV, in this case), 

     2) after a certain period of time has elapsed a startup function (if
         defined) is called.  This function can perform a task in the external app
         (e.g. show the program guide).

     2) hides FrontRow and 

     3) waits until the specified exit conditon is met (if any) before returning to Front Row

     This class also makes sure the EyeTV screenshot is up to date when returning to Front Row
       
    """

    def initWithStartup_(self, startup=None):
        log("initWithStartup_")
        self.tickCount=0
        self.startup=startup
        self.frcontroller = BRAppManager.sharedApplication().delegate()
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
        if self.tickCount == wait_before_exit_ticks: 
            AutoQuitManager = objc.lookUpClass("FRAutoQuitManager")
            AutoQuitManager.sharedManager()._stopAutoQuitTimer()
            AutoQuitManager.sharedManager().setAutoQuitEnabled_(False)

        # if not stabilized, we don't exit EyeTV
        if self.tickCount < wait_before_exit_ticks:
            return False

        # if we become visible after stabilization, then we've exited EyeTV and we need to pop
        if self.frcontroller.uiVisible():
            ETV.UpdateScreenShot()
            ETV.HideWindows()
            return True

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
        ETV.UpdateScreenShot()
        ETV.HideWindows()



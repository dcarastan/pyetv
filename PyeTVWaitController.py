import objc
from PyFR import *

import PyFR.WaitController
import PyFR.Utilities
from PyFR.BackRow import *

from etv import ETV
from Logger import *

class PyeTVWaitController(PyFR.WaitController.WaitController, PyFR.Utilities.ControllerUtilities):
    """
    A Front Row controller which 

     1) launches an external app (EyeTV, in this case), and calls any startup code

     2) hides FrontRow and 

     3) waits until the specified exit conditon is met (if any) before returning to Front Row

    """

    def initWithStartup_exitCond_(self, startup=None,exitCond=None):
        log("initWithStartup_")
        #self.tickCount=0
        self.wasHidden=False
        self.startup=startup
        self.exitCond=exitCond
        self.frcontroller = BRAppManager.sharedApplication().delegate()
        return PyFR.WaitController.WaitController.initWithText_(self, "Launching EyeTV")

    def PyFR_start(self):
        log("PyFR_start called_")
        #self.tickCount = 0
        self.wasHidden = False
        if self.startup is not None:
            self.call_startup = True
        else:
            self.call_startup = False
        self.launchApp( '/Applications/EyeTV.app')
        self.textController.setTitle_("") # don't show "Launching EyeTV" when we come back

    def AppShouldExit(self):
        if not self.frcontroller.uiVisible():
            self.wasHidden = True
            self.doStartup()
            AutoQuitManager = objc.lookUpClass("FRAutoQuitManager")
            AutoQuitManager.sharedManager()._stopAutoQuitTimer()
            AutoQuitManager.sharedManager().setAutoQuitEnabled_(False)

        # if we become visible after we've been hidden, then we've exited EyeTV and we need to pop
        if self.wasHidden and self.frcontroller.uiVisible():
            log("FR ui is visible, so hiding windows")
            self.doShutdown()
            return True

        if self.exitCond is not None and self.exitCond():
            self.doShutdown()
            return True

        return False

    def doStartup(self):
        if self.call_startup:
            try:
                log("calling PyeTVWaitController.startup()")
                self.startup()
                self.call_startup = False
            except:
                log("PyeTVWaitController.startup() failed")
                pass

    def doShutdown(self):
        #ETV.HideWindows()
        #ETV.UpdateScreenShot()
        ETV.Stop()
        #ETV.SweepDeleted()
        pass

    def AboutToHideFR(self):
        #self.doStartup()
        pass

    def FRWasShown(self):
        log("**************** FRWasShown *****************");
        try:
            # sometimes this doesn't work!
            self.doShutdown()
            self.stack().popController()
        except:
            pass



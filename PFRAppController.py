#import modules required by application
import objc
import Foundation
import AppKit

import os 
import time 
import threading

from Logger import *

# Import backrow
objc.loadBundle("BackRow", globals(), bundle_path=objc.pathForFramework("/System/Library/PrivateFrameworks/BackRow.framework" ))

class PFRAppController(BRController):
    def __setupText(self):
        ''' Set up the text field '''
        attribs = BRThemeInfo.sharedTheme().paragraphTextAttributes()
        self.textController = BRHeaderControl.alloc().init()
        self.textController.setTitle_( u"Loading %s" % self._app_name)

        # There's probably a better way to do this,
        masterFrame = BRRenderScene.singleton().size()
        w = masterFrame[0]
        h = masterFrame[1]

        origin = ( 0, 
                   (h * 0.5))

        size = ( w, h * 0.25 )
        

        # Where it goes, and how big
        self.textController.setFrame_( ( origin, size ) )

        self.addControl_(self.textController)

    def __setupSpinner(self):
        self.spinner = BRWaitSpinnerControl.alloc().init()
        self.spinner.controlWasActivated()

        masterFrame = BRRenderScene.singleton().size()

        log(masterFrame)
        w = masterFrame[0]
        h = masterFrame[1]

        origin = (w*0.25, 0)
        size = (w*0.5, h*0.5)

        self.spinner.setFrame_( ( origin, size ) )

        self.addControl_(self.spinner)

    def initWithAppPath_AppName_(self,app_path,app_name):
        log("in initWithAppPath_AppName_")
        BRController.init(self)
        
        self._app_path=app_path
        self._app_name=app_name

        self.__setupText()
        self.__setupSpinner()
        self._exit_cond_test=lambda: False
        self._user_timeout_func=None
        self._user_timeout_ticks=0

        return self

    def setExitConditionTest(self, exit_cond_test):
        log("Setting exit ftor to %s" % exit_cond_test)
        self._exit_cond_test=exit_cond_test

    def setUserTimeoutFunc(self,func,ticks):
        log("Setting timeout ftor to %s" % func)
        self._user_timeout_func=func
        self._user_timeout_ticks=ticks

    def wasPushed(self):

        # Load App
        ws = NSWorkspace.sharedWorkspace()
        ws.launchApplication_( self._app_path )
        
        # wait for App to launch
        found = False
        while not found:
            # I probably shouldn't use a sleep here, as thats not good GUI 
            # practice. But it works. Not like its going to be around long in 
            # here.
            time.sleep(.5)

            # check the list of launched app to see if App has finished loading.
            for app in NSWorkspace.sharedWorkspace().launchedApplications():
                log(app['NSApplicationName'])
                if app['NSApplicationName'] == self._app_name:
                    found = True
                    break
            if found:
                break

        # Get FR out of the way. Boy was this fun trying to figure out.
        frController = BRAppManager.sharedApplication().delegate()
        frController._hideFrontRow()
        
        # Start a timer
        self.tickCount=0
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_( 0.25, self, "tick:", None, True )

        # Make sure to call the parent!
        BRController.wasPushed(self)

    def tick_(self, senders):
        self.tickCount=self.tickCount+1

        # possilby call a single-shot-user timeout.  the user can
        # reinstall it if desired this is so that startup code that
        # needs to be run after the app is visible can be called (e.g. some apple events)
        if self._user_timeout_func is not None and \
                self.tickCount > self._user_timeout_ticks:
            a=self._user_timeout_func
            self._user_timeout_ticks=0
            self._user_timeout_func=None
            a(self)

        # Check to see if App is running.
        found = False
        for app in NSWorkspace.sharedWorkspace().launchedApplications():
            if app['NSApplicationName'] == self._app_name:

                # Is it the active app?
                ws = NSWorkspace.sharedWorkspace()

                activeApp = ws.activeApplication()
                if activeApp['NSApplicationName'] != self._app_name:

                    # ping it, so it becomes active.
                    # Why do we do this you ask? Well.. When we hide front row
                    # above, it brings the last active application to the front.
                    # Why? I don't know.
                    ws.launchApplication_( self._app_name )

                found=True
                break

        # If we don't find App running, then we exited. So bring FR back.
        if not found or self._exit_cond_test():
            frController = BRAppManager.sharedApplication().delegate()
            frController._showFrontRow()

            # Make sure to turn off the timer!
            self.timer.invalidate()



        







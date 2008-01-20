#import modules required by application
import objc
import Foundation
import AppKit

import os
import time 
import threading

# Import backrow
objc.loadBundle("BackRow", globals(), bundle_path=objc.pathForFramework("/System/Library/PrivateFrameworks/BackRow.framework" ))
objc.loadBundleFunctions(Foundation.__bundle__, globals(),[('instrumentObjcMessageSends', objc._C_VOID + objc._C_NSBOOL)])

# Logging.
def log(s):
    Foundation.NSLog( "PyeTV: %s" % str(s) )


class EnableObjcLogger():
    def __init__(self):
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_( 0.25, self, "tick:", None, True )
        
    def tick_(self, senders):
        instrumentObjcMessageSends(os.path.isfile("/tmp/FRLOG"))


#  Created by garion on 12/15/07.
#  Copyright __MyCompanyName__ 2007. All rights reserved.

#import modules required by application
import objc
import Foundation
import AppKit

import MainApp

# Import backrow
objc.loadBundle("BackRow", globals(), bundle_path=objc.pathForFramework("/System/Library/PrivateFrameworks/BackRow.framework" ))


# this class is the glue that allows us to be loaded by frontrow.
# If you want to create you own plugins, the only thing you need to change is 
# the applianceController method. 
class RUIPythonAppliance( BRAppliance ):

    sanityCheck = False

    @classmethod
    def initialize(cls):
        name = NSString.alloc().initWithString_( MainApp.GetAppKey() )
        BRFeatureManager.sharedInstance().enableFeatureNamed_( name )

    @classmethod
    def className(cls):

        clsName = NSString.alloc().initWithString_( cls.__name__ )

        backtrace = BRBacktracingException.backtrace()
        range = backtrace.rangeOfString_( "_loadApplianceInfoAtPath:" )

        if range.location == Foundation.NSNotFound and cls.sanityCheck == False:
            range = backtrace.rangeOfString_( "(in BackRow)" )
            cls.sanityCheck = True
        
        if range.location != Foundation.NSNotFound:
            clsName = NSString.alloc().initWithString_( "RUIMoviesAppliance" )

        return clsName

    def applianceController(self):
        return MainApp.GetAppController();


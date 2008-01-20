#
#  PFROptionDialog.py
#
#  Created by jchrist on 1/10/08

#import modules required by application
import objc
import Foundation
import AppKit

from Logger import *

# Import backrow
objc.loadBundle("BackRow", globals(), bundle_path=objc.pathForFramework("/System/Library/PrivateFrameworks/BackRow.framework" ))

class PFROptionDialog(BROptionDialog):
    def initWithTitle_Items_Handler_UserData_(self,title,items,handler,userdata):
        log("init PFROptionDialog")
        BROptionDialog.init(self)
        self.setTitle_(title)
        for i in items:
            self.addOptionText_(i)
        self.setActionSelector_target_("response:", self)
        self.handler=handler
        self.userdata=userdata
        return self

    def response_(self):
        log("got response")
        if self.handler(self,self.selectedIndex(),self.userdata):
            self.stack().popController()

# 
# example of using a PFROptionDialog:  
#    PFROptionDialogTest creates & pushes a dialog with prompts 1,2,3 and userdata [a,b,c]
#
# if the dialog is responded to (i.e. not backed out of), PFROptionDialogHandler will be 
# called with the index of the selected menu item and the userdata can be displayed
#

def testPFROptionDialogHandler(controller,idx,userdata):
    log("_PFROptionDialogHandler got result %d, with userdata[%s] " % (idx,userdata[idx]))
    alert = BRAlertController.alertOfType_titled_primaryText_secondaryText_( 0, "Option response:", "Option #%s" % str(idx), "Userdata: %s" % str(userdata[idx]))
    controller.stack().pushController_(alert)

    # if we return true, we'll pop the controller and back up past the option dialog
    return False

def testPFROptionDialogTest(controller,arg):
    log("in _PFROptionDialogTest")
    dlg=PFROptionDialog.alloc().initWithTitle_Items_Handler_UserData_("Test options",["Select a1","Select b","Select c"],testPFROptionDialogHandler,["a","b","c"])
    return controller.stack().pushController_(dlg)

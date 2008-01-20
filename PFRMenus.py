#  Created by garion on 12/15/07.
#  Copyright __MyCompanyName__ 2007. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from Logger import *

# Import backrow
objc.loadBundle("BackRow", globals(), bundle_path=objc.pathForFramework("/System/Library/PrivateFrameworks/BackRow.framework" ))

# in individual menu item with text, a function to be called when activated, and an optionional argument to be passed to the function
class PFRMenuItem:
      def __init__(self,title,func,arg=None,subtitle=""):
            self.title=title
            self.subtitle=subtitle
            self.func=func
            self.arg=arg

      def Activate(self, controller):
          log("In activate for %s" % self.title)
          self.func(controller, self.arg)

# simple container class for a menu, elements of the items list may contain menu items or another PFRMenu instance for submenus
class PFRMenu:
      def __init__(self,page_title,items=[],subtitle=""):
          self.page_title=page_title
          self.items=items
          self.subtitle=subtitle
          
      def AddItem(self,item):
          self.items.append(item)

# used to duck-type PFRMenus (to indicate an item is a submenu)
def IsPFRMenu(a):
      return hasattr(a,'page_title')

BRMenuListItemProvider = objc.protocolNamed('BRMenuListItemProvider')
class PFRMenuDataSource(NSObject, BRMenuListItemProvider):
    def init(self):
        log("datasource init");
        self._names = [("Item 1",True), 
                       ("Item 2",True), 
                       ("Item 3",False)]
        return NSObject.init(self)

    def initWithController_Menu_(self, ctrlr, menu):
        self.ctrlr = ctrlr
        self.menu = menu
        return self.init()

    def itemCount(self):
        log("Item count requested, returning %d" % len(self.menu.items))
        return len(self.menu.items)
  
    def titleForRow_(self,row):
        log("Title for row %d requested" % row)
        if row >= len(self.menu.items):
            return None
        if IsPFRMenu(self.menu.items[row]):
              return self.menu.items[row].page_title
        else:
              return self.menu.items[row].title
    
    def itemForRow_(self,row):
        log("Item for row %d requested" % row)
        if row >= len(self.menu.items):
            return None

        if IsPFRMenu(self.menu.items[row]):
            if self.menu.items[row].subtitle == "":  
                  result=BRTextMenuItemLayer.folderMenuItem()
                  result.setTitle_(self.menu.items[row].page_title)
            else:
                  # note, this should work but doesn't as the title obscures the subtitle!
                  result=BRTwoLineTextMenuItemLayer.alloc().init()
                  result.setTitle_(self.menu.items[row].page_title) # FIXME: use folder icon!?
                  result.setSubtitle_(self.menu.items[row].subtitle)
        else:
            if self.menu.items[row].subtitle == "":  
                  result=BRTextMenuItemLayer.menuItem()
            else:
                  # note, this should work but doesn't as the title obscures the subtitle!
                  result=BRTwoLineTextMenuItemLayer.alloc().init()
                  result.setSubtitle_(self.menu.items[row].subtitle)
            result.setTitle_(self.menu.items[row].title)
        log("returning item for row %d" % row)
        return result

    def itemSelected_(self, row):
        log("Item for row %d selected" % row)
        if IsPFRMenu(self.menu.items[row]):
            log("Submenu %s selected" % self.menu.items[row].page_title)
            con = PFRMenuController.alloc().initWithMenu_(self.menu.items[row])
            self.ctrlr.stack().pushController_(con)
        else:
            log("Menu item %s selected" % self.menu.items[row].title)
            self.menu.items[row].Activate(self.ctrlr)


    # Dont care aboutr these below.
    def heightForRow_(self,row):
        return 0.0

    def rowSelectable_(self, row):
        return True

class PFRMenuController(BRMenuController):

    def initWithMenu_(self, menu):
        log("in rmcinit2 for menu %s" % menu.page_title)
        BRMenuController.init(self)
        self.setListTitle_( menu.page_title )
        self.ds = PFRMenuDataSource.alloc().initWithController_Menu_(self,menu)
        self.list().setDatasource_(self.ds)
        return self

    def willBePushed(self):
        self.list().reload()
        BRMenuController.willBePushed(self)

    def itemSelected_(self, row):
        self.ds.itemSelected_(row)

    def rowSelectable_(self,row):
        return True




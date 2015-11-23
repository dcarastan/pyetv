
```
#
# classes to deal with recording metadata previews (screenshots, description text, etc)
#

import objc
import string
from PyFR.BackRow import *
from etv import ETV
import Foundation

from translate import tr


# This is a simplified version which only works for "recordings", not channels or series,
# and should be easier to understand.  Warning, I haven't tested this version...it's for
# instructional purposes only.

# Overview:  
#
#  This is the result of much trial and error, and parts of it are hairy...
#
#  basically each menu item on the right has an associated "asset" class
#  which knows how to get the metadata to be displayed.
#
#  so, reading the code from the bottom up:
#
#   1) A metadata controller is created (elsewhere) for a given menu item
#        here, that item is a "rec" (recording object, which is used to look
#        up what metadata to display
#
#   2) FR itself will call _updateMetadataLayer when needed.
#      this does some magic to replace the stock metadata populator
#      (which I never could figure out) with the fake one here (PyeTVMetadataPopulatorFactory)
#
#   3) our populator (PyeTVMetadataPopulator) sets the text fields displayed based on the 'asset'
#
#   4) our asset (PyeTVMediaAsset) stores a reference to the recording (for use by the populator to look up titles, etc)
#      this asset has the coverArt function which is called to display the image for the recording.
#



verbose=0
def log(s,level=1):
    if verbose >= level:
        Foundation.NSLog( u"%s: %@", "PyeTV", s )
    pass


#
# An 'asset' is required to display metadata for the currently selected menu item
#
# this asset has a coverArt function which gets the image to display from the recording object
#

class PyeTVMediaAsset(BRSimpleMediaAsset):
    """
    Defines a FrontRow media asset from a EyeTV recording  
    """
    def initWithRecording_(self, rec):
        log("PyeTVMediaAsset inited for rec %s" % rec.GetTitle().encode("ascii","replace"))
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.rec=rec
        self.firstTime=True
        return self

    def coverArt(self):
        log("PyeTVMediaAsset::coverArt")
        return BRImage.imageWithPath_(self.rec.GetPreviewImagePath())

    # the first time this is called, it's apparently being asked if it conforms to a BRMediaAsset protocol.  The next time, a collection.
    def conformsToProtocol_(self, protocol):
         log("PyeTVMediaAsset::conformsToProtocol: %s" % repr(protocol))
         if self.firstTime:
             self.firstTime=False
             return True
         return False




class PyeTVMetadataPopulator(NSObject):
    """
    The populator class to be returned by PyeTVMetadataPopulatorFactor
    """

    def populateLayer_fromAsset_(self, layer, asset):
        # FR will call this function when it needs to update the metadata for a given 'asset'
        #
        # this function sets the text to be displayed as the metadata fields.
        # you can set a title, a summary, and various other labeled data, based on the 'asset'
        #
        # you'll need to customize this to display the information you want based on your asset.

        #log("We want to do magic stuff here for layer %s and asset %s" % (repr(layer), repr(asset)))
        layer.setTitle_(asset.rec.GetTitle())
        layer.setSummary_(asset.rec.GetDescription())
        labels=[
            tr("Episode"),
            tr("Channel"),
            tr("Position"),
            tr("Recorded at")
            ]
        data=[
            asset.rec.GetEpisode(),
            asset.rec.GetChannelStr(),
            asset.rec.GetPlaybackPosition(True) + " / " +asset.rec.GetDuration(True),
            asset.rec.GetStartTime()
            ]
        layer.setMetadata_withLabels_(data,labels)
        return

    def axMetadataFromAsset_(self, asset):
        log("called axMetadataFromAsset %s" % repr(asset))
        return None


#
#
# This is deep, dark magic which tricks front row into using our own populator
# instead of the built-in one.  Don't try to understand this...I barely do myself.
# Luckly, you can probably use it without much if any change.
#

class PyeTVMetadataPopulatorFactory(BRSingleton):
    """
    Custom metadata populator factory which will return a populator which understands EyeTV recordings
    """

    __Instance = None

    def init(self):
        log("initing Populator factory",0)
        self=super(PyeTVMetadataPopulatorFactory,self).init()
        if self is None:
            return None
        __Instance=self
        self.pop=PyeTVMetadataPopulator.alloc().init()
        return self

    # Note: this isn't really a good singleton implementation, but it's good enough for our purposes here
    @classmethod
    def singleton(self):
        log("returning populator singleton",0)
        return self.__Instance

    def populatorForAsset_(self, asset):
        return self.pop

# create instance of this to use below
newPopFactory=PyeTVMetadataPopulatorFactory.alloc().init()


#
#  End of deep magic
#




class PyeTVPreviewMetadataController(BRMetadataPreviewController):
    """
    A Front Row controller which shows a preview based on metadata from a EyeTV recording
    """

    def initWithRecording_(self, rec):
        #
        # create and set an "asset" which know what metadata to display
        # here, the asset is a PyeTVMediaAsset for a given recording, but you
        # could change that

        log("metadataController::initWithRecording_ %s" % repr(self))
        self=super(PyeTVPreviewMetadataController,self).init()
        if self is None:
            return None
        asset=PyeTVMediaAsset.alloc().initWithRecording_(rec)
        self.setAsset_(asset)
        self.setShowsMetadataImmediately_(True) # could comment this out for a bigger look at the screenshot, but the md is more important
        return self

    def _updateMetadataLayer(self):
        #
        # you probably won't need to change this
        #
        log("PyeTVPreviewMetadataLayerController::_updateMetadataLayer")

        # The standard populator doesn't understand our assets, so we
        # temporarily replace the std populator factory with our populator
        # factory.  (and yes, this is a horrible abuse of setSingleton_.)
        #
        # Here is where we use the deep, dark magic classes above.

        oldPopFactory=BRMetadataPopulatorFactory.sharedInstance()
        BRMetadataPopulatorFactory.setSingleton_(newPopFactory)
        BRMetadataPreviewController._updateMetadataLayer(self)
        BRMetadataPopulatorFactory.setSingleton_(oldPopFactory)

    def dealloc(self):
        #
        # you probably won't need to change this
        #
        log("PyeTVPreviewMetadataLayerController::_updateMetadataLayer")

        log("metadataController dealloc for %s" % repr(self))
        if self.asset() is not None:
            log("releasing asset %s" % repr(self.asset()))
            #self.asset().release()
        super(PyeTVPreviewMetadataController,self).dealloc()

```
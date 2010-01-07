#
# classes to deal with recording metadata previews (screenshots, description text, etc)
#

import objc
import string
from PyFR.BackRow import *
from etv import ETV
import Foundation

from translate import tr


verbose=0
def log(s,level=1):
    if verbose >= level:
        Foundation.NSLog( u"%s: %@", "PyeTV", s ) 
    pass

class PyeTVMediaAsset(BRSimpleMediaAsset):
    """
    Defines a FrontRow media asset from a EyeTV recording  
    """
    def initWithRecording_(self, rec):
        log("PyeTVMediaAsset inited for rec %s" % rec.GetTitle().encode("ascii","replace"))
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.channel=None
        self.rec=rec
        self.firstTime=True
        self.IsSeries=False
        self.IsChannel=False
        return self

    def initWithSeriesEpisode_(self, rec):
        log("PyeTVMediaAsset inited for rec %s" % rec.GetTitle().encode("ascii","replace"))
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.channel=None
        self.rec=rec
        self.firstTime=True
        self.IsSeries=True
        self.IsChannel=False
        return self

    def initWithChannel_(self, chan):
        log("PyeTVMediaAsset inited for channel %s" % repr(chan).encode("ascii","replace"))
        BRSimpleMediaAsset.initWithMediaURL_(self,"")
        self.rec=None
        self.channel=chan
        self.firstTime=True
        self.IsSeries=False
        self.IsChannel=True
        return self

    def coverArt(self):
        log("PyeTVMediaAsset::coverArt")
        if self.IsChannel:
            return BRImage.imageWithPath_(self.channel.GetPreviewImagePath())
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
    def populateChannelData(self, layer, asset):
        log("in populateChannelData")

        currentTitle=""
        nextDesc=""
        nextTime=""
        nextTitle=""
        currentDesc=""

        recording,data=asset.channel.GetProgramInfo()
        log("%s, %s" % (str(recording).encode("ascii","replace"),str(data).encode("ascii","replace")))
        if not data:
            return
        if not recording and not data.has_key('currentShow'):
            return
        if recording:
            c=ETV.RecordingChannelName()
            log("Got recording, channel name %s" % c)
            if c is None:
                return
            currentTitle=tr("Now Recording!")
            currentDesc=(tr("Currently recording channel %s.  Program info is not available.") % c)

        try:
            currentShow=data['currentShow']
            currentTitle += currentShow['title'] 
            if currentShow.has_key('shortDescription'):
                currentDesc += currentShow['shortDescription'] + " "
            currentDesc += currentShow['startTime'].strftime("%I:%M") + "-" + currentShow['endTime'].strftime("%I:%M%p") 
        except:
            pass
        try:
            nextShow=data['nextShow']
            nextTitle = nextShow['title']
            nextTime = nextShow['startTime'].strftime("%I:%M%p") + "-" + nextShow['endTime'].strftime("%I:%M%p")
            nextDesc = nextShow['shortDescription']
        except:
            pass

        layer.setTitle_(currentTitle)
        layer.setSummary_(currentDesc)
        labels=[
            tr("Next"),
            tr("Episode"),
            tr("At")
            ]
        data=[
            nextTitle,
            nextDesc,
            nextTime
            ]
        layer.setMetadata_withLabels_(data,labels)

    def populateLayer_fromAsset_(self, layer, asset):
        #log("We want to do magic stuff here for layer %s and asset %s" % (repr(layer), repr(asset)))
        if asset.IsSeries:
            return
        if asset.IsChannel:
            self.populateChannelData(layer,asset)
            return
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

class PyeTVPreviewMetadataController(BRMetadataPreviewController):
    """
    A Front Row controller which shows a preview based on metadata from a EyeTV recording
    """

    def initWithRecording_(self, rec):
        log("metadataController::initWithRecording_ %s" % repr(self))
        self=super(PyeTVPreviewMetadataController,self).init()
        if self is None:
            return None
        asset=PyeTVMediaAsset.alloc().initWithRecording_(rec)
        self.setAsset_(asset)
        self.setShowsMetadataImmediately_(True) # could comment this out for a bigger look at the screenshot, but the md is more important
        return self

    def initWithSeriesEpisode_(self, rec):
        log("metadataController::initWithSeriesEpisode_ %s" % repr(self))
        self=super(PyeTVPreviewMetadataController,self).init()
        if self is None:
            return None
        asset=PyeTVMediaAsset.alloc().initWithSeriesEpisode_(rec)
        self.setAsset_(asset)
        #self.setShowsMetadataImmediately_(True) 
        return self

    def initWithChannel_(self, channel):
        log("metadataController::initWithChannel_: %s" % repr(self))
        self=super(PyeTVPreviewMetadataController,self).init()
        if self is None:
            return None
        asset=PyeTVMediaAsset.alloc().initWithChannel_(channel)
        self.setAsset_(asset)
        self.setShowsMetadataImmediately_(True) 
        return self

    def _updateMetadataLayer(self):
        log("PyeTVPreviewMetadataLayerController::_updateMetadataLayer")

        # The standard populator doesn't understand our assets, so we
        # temporarily replace the std populator factory with our populator
        # factory.  (and yes, this is a horrible abuse of setSingleton_.)

        oldPopFactory=BRMetadataPopulatorFactory.sharedInstance()
        BRMetadataPopulatorFactory.setSingleton_(newPopFactory)
        BRMetadataPreviewController._updateMetadataLayer(self)
        BRMetadataPopulatorFactory.setSingleton_(oldPopFactory)

    def dealloc(self):
        log("metadataController dealloc for %s" % repr(self))
        if self.asset() is not None:
            log("releasing asset %s" % repr(self.asset()))
            #self.asset().release()
        super(PyeTVPreviewMetadataController,self).dealloc()



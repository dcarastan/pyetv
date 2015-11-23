![http://lh4.ggpht.com/jon.christopher/SAbyRNddqqI/AAAAAAAAA4Q/zAK1ofosBU0/s320/img1.jpg](http://lh4.ggpht.com/jon.christopher/SAbyRNddqqI/AAAAAAAAA4Q/zAK1ofosBU0/s320/img1.jpg)
![http://lh4.ggpht.com/jon.christopher/SAbySNddquI/AAAAAAAAA4w/HsApkh5DRyE/s320/img5.jpg](http://lh4.ggpht.com/jon.christopher/SAbySNddquI/AAAAAAAAA4w/HsApkh5DRyE/s320/img5.jpg)

# PyeTV #

This plugin allows access to [EyeTV](http://www.elgato.com/) from within Front Row on Leopard, adding a EyeTV item to Front Row's top level menu.  The plugin gives access to EyeTV's recordings (grouped by series), along with an image preview and recording metadata.

PyeTV also integrates with [ETVComskip](http://code.google.com/p/etv-comskip), a Mac OS X port of comskip (http://www.kaashoek.com/comskip/) designed to work with EyeTV.  ETVComskip allows users of EyeTV to enjoy commercial-free recorded television.  PyeTV provides capabilities of turning commercial skipping on and off from within Front Row, as well as starting a commercial search for recordings which do not have commercial markers already. **You will have to install ETVComskip separately if you want this functionality.**


## Installation ##

Download the .dmg file.  Double click to open the .dmg file and run the installer application.  The installer will prompt for an administrator's password (because it needs to be installed in /Library).  Further, if you do not have "Enable access for assistive devices" turned on in the Universal access preference pane, the installer will attempt to do that for you after another password prompt.

A few users have reported problems with the .dmg file. In this case, make sure that the extension on the file is .dmg and try again to open it.  This should resolve the problem.

## Special Note for Snow Leopard and EyeTV 3.2.1 ##

The 10.6.2 update to Snow Leopard broke the usage of the Apple remote to control EyeTV.
Until there is an update to EyeTV, the default remote driver will not work.  The work around I've found us to install the Candleair driver from: http://www.iospirit.com/labs/candelair/, and enable Leopard combatibility mode in the corresponding preference pane.

# News #

## May 25, 2010 ##
Updated to work with EyeTV 3.4.

## Nov 28, 2009 ##

Version 2.0 released, with Snow Leopard support.

This version also includes support for the favorite channels playlist.




## Oct 24, 2008 ##

Version 1.2 released!  Changes include

  * The channels list now has program info as metadata, if it's available from EyeTV.

  * Cleaner interaction with EyeTV.  We no longer return to PyeTV on "pause" but only on "menu" which makes it possible to pause live tv, etc.

  * Problems switching back and forth between watching live tv and recorded programs are resolved.

  * EyeTV windows closed when Front Row exits

  * Improved Program guide access.

  * Can now handle non-ascii characters in recording titles.

See [Version\_1\_2\_Changelog](Version_1_2_Changelog.md) for details.


## Apr 16, 2008 ##

Version 1.1 released.  This version features image previews of the recordings, and has a very similar look to browsing the music library in Front Row.  The recordings list is cleaned up slightly, sorted by date, and the recordings are shown in a slightly smaller font to allow for longer episode titles to be seen without scrolling.


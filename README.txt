CHANGES:

Version 1.2:

   The channels list now has program info as metadata, if it's available
   from EyeTV.  

   Cleaner interaction with EyeTV.  We no longer return to PyeTV on
   "pause" but only on "menu" which makes it possible to pause live tv,
   etc.  Problems switching back and forth between watching live tv and
   recorded programs are resolved.

   EyeTV windows are automatically closed when leaving Front Row, showing
   the user's desktop.  Many users have requested this, particularly since
   Live TV windows were somewhat problematic before.

   The "Program guide" function is now much more useful, as PyeTV no
   longer returns control from EyeTV to Front Row as soon as the guide is
   dismissed.  This means that you can use the program guide to select a
   show you want to watch, and then watch it.

   The somewhat useless "Enter EyeTV" menu option has been removed, as playing a
   channel or showing the program guide will have the same effect.

   Code cleanups and time delays have been reduced, where possible, resulting in
   faster response times when switching from EyeTV to FR and vice versa.

   Problems where Front Row would quit if EyeTV had been running for a
   long time (more than 20 min), meaning that you would not return to the
   same place in Front Row when you returned (via pressing menu) have been
   resolved.

   Fixed bug dealing with unicode characters in recording titles
   (e.g. accented characters, umlauts, etc.)  Should behave much better
   for international users now.


DEVELOPERS:
   First, make sure py-appscript is installed http://appscript.sourceforge.net/

   You may get the PyeTV sources from google code's svn.  

   To build:

  	 Type "make real" in from the PyeTV directory.
  	 sudo mv dist/EyeTV.frappliance /System/Library/CoreServices/Front\ Row.app/Contents/PlugIns/


     Instead of typing "make real", you may wish to type "make link".
     ln -sf /path/to/PyeTV/dist/EyeTV.frappliance /System/Library/CoreServices/Front\ Row.app/Contents/PlugIns/
     
     NOTE: In both cases you will need to restart Front Row before the plugin will show up.  

     "make" with no arguments will kill Front Row, so that the next invocation of Front Row will
     pick up any changes you've made to PyeTV.


OUTSTANDING ISSUES:

     EyeTV must be running before Front Row is started.

     We have to expose the desktop (hide Front Row) *before* we can
     tell EyeTV to go full screen, so the transition between FR and
     EyeTV is somewhat ugly.

LICENSE:
	These files are placed under the BSD license.

ACKNOWLEDGEMENTS:

	This work was made possible by the FrontPython project, and
        would literally not have been possible without it.

           http://code.google.com/p/frontpython/

        Special thanks to garionPHX of that project for all his
        assistance.


	FrontPython, in turn, made use of techniques developed by the
	fine folks at the Sapphire project: http://appletv.nanopi.net/.
	If you're not using Sapphire, you should be!


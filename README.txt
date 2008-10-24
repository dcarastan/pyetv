INSTALLATION:

     From sources (probably requires developer's tools to be installed):
         First, make sure py-appscript is installed http://appscript.sourceforge.net/
	 Type "make real" in from the PyeTV directory.
	 sudo mv dist/EyeTV.frappliance /System/Library/CoreServices/Front\ Row.app/Contents/PlugIns/


     Binary: move dist/EyeTV.frappliance to /System/Library/CoreServices/Front\ Row.app/Contents/PlugIns/
	If you do this from the Finder, you will need to use an
	option-click on Front Row.app and choose "Show package
	contents" to see the Contents directory.


     NOTE: In both cases you will need to restart Front Row before the plugin will show up.  

           bash$  sudo killall Front\ Row

     EyeTV should be running *before* invoking Front Row.


DEVELOPERS:
     
    Instead of typing "make real", you may wish to type "make link".
    ln -sf /path/to/PyeTV/dist/EyeTV.frappliance /System/Library/CoreServices/Front\ Row.app/Contents/PlugIns/
     

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


-- uninstall old version
try
  do shell script "/bin/rm -rf /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns/EyeTV.frappliance" with administrator privileges
end try

--install new version
tell application "Finder"
	set path_ to (folder of file (path to me)) as string
	set path_ to POSIX path of path_
end tell
do shell script "cp -Rfp " & path_ & "/EyeTV.frappliance /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns" with administrator privileges

--copy icon from EyeTV application
try
  do shell script "cp /Applications/EyeTV.app/Contents/Resources/eyetv.icns /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns/EyeTV.frappliance/Contents/Resources/ApplianceIcon.png" with administrator privileges
on error
  display dialog "Could not find EyeTV icon, you won't have a pretty EyeTV icon."
end try

--terminate Front Row so that it will pick up changes
do shell script "killall Front\\ Row 2>/dev/null; /usr/bin/true"

display dialog "PyeTV is now installed.

In order for the EyeTV program guide to be accessable to PyeTV, we need to enable GUI scripting in the Universal Access preference pane.

If GUI scripting is is not currently enabled, the installer will ask for your user password in order to turn it on." buttons {"Ok"}

try
tell application "AppleScript Utility"
     set GUI Scripting enabled to true
end tell
on error
   display dialog "Error enabling GUI scripting, program guide will not be available until turned on in the Universal Access preferences."
end try



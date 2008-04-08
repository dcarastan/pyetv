-- uninstall old version
do shell script "/bin/rm -rf /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns/EyeTV.frappliance" with administrator privileges

--install new version
tell application "Finder"
	set path_ to (folder of file (path to me)) as string
	set path_ to POSIX path of path_
end tell
do shell script "cp -Rfp " & path_ & "/EyeTV.frappliance /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns" with administrator privileges

--copy icon from EyeTV application
do shell script "cp /Applications/EyeTV.app/Contents/Resources/eyetv.icns /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns/EyeTV.frappliance/Contents/Resources/ApplianceIcon.png" with administrator privileges

--terminate Front Row so that it will pick up changes
do shell script "killall Front\\ Row"

display dialog "PyeTV installed" buttons {"Ok"}

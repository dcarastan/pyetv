try
  do shell script "/bin/rm -rf /System/Library/CoreServices/Front\\ Row.app/Contents/PlugIns/PyeTV.frappliance" with administrator privileges

  --terminate Front Row so that it will pick up changes
  do shell script "killall Front\\ Row 2>/dev/null; /usr/bin/true"

  display dialog "PyeTV uninstalled" buttons {"Ok"}

on error
  display dialog "Error uninstalling PyeTV." buttons {"Weird"}
end try



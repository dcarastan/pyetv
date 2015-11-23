# PyeTV version 1.2 #

The channels list now has program info as metadata, if it's available from EyeTV.

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
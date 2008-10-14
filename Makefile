NAME=PyeTV
VERSION=1.2
IMGNAME=${NAME}-${VERSION}

kill:
#	python setup.py py2app -A
	-kill `ps -aex | grep "Front Row" | awk '{print $$1}'`
	-kill `ps -aex | grep Screen | awk '{print $$1}'`
	-killall ScreenSaverEngine
	-killall ScreenSaverEngine


clean::
	rm -rf build dist

real: clean
	python setup.py py2app

link: clean
	python setup.py py2app -A

test:
	python test.py

tar:
	pushd ..; tar -czvf ${IMGNAME}.tar.gz PyeTV; popd

installers: real
	osacompile -o dist/Install\ PyeTV.app Install.applescript
	osacompile -o dist/UnInstall\ PyeTV.app UnInstall.applescript

dmg: installers
		cd dist; rm *.dmg*; hdiutil create -fs HFS+ -format UDBZ -volname ${IMGNAME} -srcfolder . ${IMGNAME}

dist:  clean real dmg

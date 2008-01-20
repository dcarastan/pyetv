kill:
#	python setup.py py2app -A
	kill `ps -aex | grep "Front Row" | awk '{print $$1}'`
	kill `ps -aex | grep Screen | awk '{print $$1}'`

clean:
	rm -rf build dist

real: clean
	python setup.py py2app

link: clean
	python setup.py py2app -A

test:
	python test.py

tar:
	pushd ..; tar -czvf PyeTV-${VERSION}.tar.gz PyeTV; popd

dist:  real tar

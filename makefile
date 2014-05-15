show:
	echo 'Run "make install" as root to install program!'
	
run:
	python hackbox-darknet-setup.py
install:
	sudo cp hackbox-darknet-setup.py /usr/bin/hackbox-darknet-setup
	sudo chmod +x /usr/bin/hackbox-darknet-setup
uninstall:
	sudo rm /usr/bin/hackbox-darknet-setup
installed-size:
	du -sx --exclude DEBIAN ./debian/
build: 
	sudo make build-deb;
build-deb:
	mkdir -p debian;
	mkdir -p debian/DEBIAN;
	mkdir -p debian/usr;
	mkdir -p debian/usr/bin;
	# make post and pre install scripts have the correct permissions
	chmod 775 debdata/*
	# copy over the binary
	cp -vf hackbox-darknet-setup.py ./debian/usr/bin/hackbox-darknet-setup
	# make the program executable
	chmod +x ./debian/usr/bin/hackbox-darknet-setup
	# start the md5sums file
	md5sum ./debian/usr/bin/hackbox-darknet-setup > ./debian/DEBIAN/md5sums
	# create md5 sums for all the config files transfered over
	sed -i.bak 's/\.\/debian\///g' ./debian/DEBIAN/md5sums
	rm -v ./debian/DEBIAN/md5sums.bak
	cp -rv debdata/. debian/DEBIAN/
	chmod -Rv go+r debian/
	dpkg-deb --build debian
	cp -v debian.deb hackbox-darknet_UNSTABLE.deb
	rm -v debian.deb
	rm -rv debian

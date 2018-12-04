version = 0.1.0

deb:
	mkdir -p build/usr/lib/cgi-bin
	cp armbox.py build/usr/lib/cgi-bin/armbox.cgi
	chmod +x build/usr/lib/cgi-bin/armbox.cgi

	fpm	-t deb -s dir -C build			\
		-n armbox -v $(version) 		\
		-a noarch				\
		-d python 				\
		-d python-bottle			\
		-d python-jinja2			\
		-d qemu-system-arm			\
		-d gcc-arm:i386				\
		-d "apache | httpd"			\
		--description 'Poke and learn ARM instructions.' \
		.


clean:
	rm -fr build
	rm -f *.deb
	rm -f *.pyc

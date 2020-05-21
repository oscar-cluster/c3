DESTDIR=
PKGDEST=.
SOURCEDIR=/usr/src/redhat/SOURCES
AUTOMAKE_OPTIONS = -Wno-portability
VERSION_MAJOR= $(shell ./dist/get-version.sh ./VERSION --major)
C3_BASENAME=c3-$(shell ./dist/get-version.sh ./VERSION --full)
C3_RPM_TMPDIR=/tmp/c3_tmpdir_redhat
PREFIX=$(DESTDIR)$(prefix)
BINDIR=$(PREFIX)/usr/bin
CONTRIBDIR=$(PREFIX)/contrib
DOCDIR=$(PREFIX)/doc
MANDIR=$(DOCDIR)/man
CONFIGDIR=$(PREFIX)/etc/profile.d
FILTERDIR=$(PREFIX)/usr/bin


BINARIES  =   src/c3_com_obj.py \
              src/c3_except.py \
              src/c3_file_obj.py \
              src/c3_sock.py \
			  src/c3_config.py \
              src/cexec \
              src/cexecs \
              src/cget \
              src/ckill \
              src/ckillnode \
              src/clist \
              src/cname \
              src/cnum \
              src/cpush \
              src/cpushimage \
              src/crm \
              src/cshutdown \
              src/c3_version.py 

EXTRA_DIST	= $(BINARIES) \
			   src/ckillnode.in \
			   man/Makefile \
               man/man1/c3.1 \
               man/man1/cexec.1 \
               man/man1/cget.1 \
               man/man1/ckill.1 \
               man/man1/clist.1 \
               man/man1/cname.1 \
               man/man1/cnum.1 \
               man/man1/cpush.1 \
               man/man1/crm.1 \
               man/man4/cpushimage.4 \
               man/man4/cshutdown.4 \
               man/man5/c3.conf.5 \
               man/man5/c3-range.5 \
               man/man5/c3-scale.5 \
               contrib/add_user \
               contrib/c3cmd-filter \
               contrib/c3_conf_manager \
               contrib/cexec_mpd \
               contrib/cexec_sss \
               contrib/enable_clusters \
               contrib/Makefile \
               contrib/push_passwd \
               contrib/README \
               contrib/sync_date \
               C3-VERSION \
               debian/control \
               debian/rules \
               debian/changelog \
               debian/compat \
               debian/copyright \
               dist/get-version.sh \
               rpm/c3.spec \
               VERSION

EXTRA_DIST += doc/KNOWN_BUGS \
              doc/README.devel  \
              doc/README.scale  \
              doc/README.c3_com_obj \
              doc/README.c3_file_obj


install-exec-local: install-c3 \
				install-ckillnode \
				install-profiled \
				install-c3cmd-filter \
                install-contrib

install-c3: install-man
	echo "Install C3 files..."
	install -d $(DOCDIR)
	install -m 644 ./INSTALL ./doc/KNOWN_BUGS ./README ./ChangeLog $(DOCDIR)
	install -d $(BINDIR)
	install -m 755 $(BINARIES) $(BINDIR)

install-contrib:
	echo "Installing C3 contrib files..."
	cd contrib; make install PREFIX=$(BINDIR)

install-man: 
	echo "Installing C3 man pages..."
	cd man; make install DESTDIR=$(DESTDIR) PREFIX=$(MANDIR) 

install-ckillnode: 
	echo "Installing C3 ckillnode..."
	install -d $(BINDIR)
	install -m 755 src/ckillnode $(BINDIR)

 #
 # FIXME: TJN Hack to fixup the path in profiled scripts c3.{sh,csh}
 #        This is the problem with "//usr/bin" and "//doc/man" 
 #        b/c the prefix is "/".   TJN Added for v5.1.3.
 #
install-profiled-hack: 
	echo "XXX: HACK to fixup the profiled env files (see Makefile coments)"
	sed 's|\/\/usr|\/usr|g' < src/c3.sh > src/c3.sh.$$
	mv src/c3.sh.$$ src/c3.sh
	sed 's|\/\/doc|\/doc|g' < src/c3.sh > src/c3.sh.$$
	mv src/c3.sh.$$ src/c3.sh
	sed 's|\/\/usr|\/usr|g' < src/c3.csh > src/c3.csh.$$
	mv src/c3.csh.$$ src/c3.csh
	sed 's|\/\/doc|\/doc|g' < src/c3.csh > src/c3.csh.$$
	mv src/c3.csh.$$ src/c3.csh

install-profiled: install-profiled-hack
	echo "Installing env files..."
	install -d $(CONFIGDIR)
	install -m 755 src/c3.*sh $(CONFIGDIR)

install-c3cmd-filter:
	echo "Installing c3 cmd filter..."
	install -d $(FILTERDIR)
	install -m 755 contrib/c3cmd-filter $(FILTERDIR)

clean-local: clean-c3cmd-filter clean-profiled clean-version
	rm -rf $(PREFIX)
	rm -f `find . -name *pyc`

clean-c3cmd-filter:
	rm -f $(FILTERDIR)/c3cmd-filter

clean-profiled:
	rm -f $(CONFIGDIR)/c3.*sh

clean-version:
	rm -f C3-VERSION


clean-release: distclean  clean-scratch  clean-c3-rpm-tmpdir


clean-scratch: clean 
	rm -f src/c3_version.py \
	      src/ckillnode
	rm -f configure  \
	      Makefile.in \
	      config.log \
	      config.status \
	      missing \
	      aclocal.m4 \
	      install-sh
	rm -f build-stamp \
	      configure-stamp 
	rm -rf debian/c3-c3cmd-filter 
	rm -rf debian/files 
	rm -rf debian/c3 
	rm -rf debian/c3-ckillnode 
	rm -rf debian/c3*.log
	rm -rf debian/c3-contrib/
	rm -rf autom4te.cache


dist-rpm: dist setup-c3-rpm-tmpdir
	-@echo ""
	-@echo "Generating RPM files..."
	-@echo ""
	cp -f ${C3_BASENAME}.tar.gz   ${C3_RPM_TMPDIR}/SOURCES/
	tar -O -zxf ${C3_BASENAME}.tar.gz \
			${C3_BASENAME}/rpm/c3.spec \
			>  ${C3_RPM_TMPDIR}/SPECS/c3.spec
	rpmbuild --define "_topdir ${C3_RPM_TMPDIR}/" \
			-ba ${C3_RPM_TMPDIR}/SPECS/c3.spec
	cp -f  ${C3_RPM_TMPDIR}/RPMS/*/c3-*.rpm $(PKGDEST) 
	cp -f  ${C3_RPM_TMPDIR}/SRPMS/c3-*.rpm $(PKGDEST)

rpm: dist-rpm

setup-c3-rpm-tmpdir:
	-@echo ""
	-@echo "Setup temporary RPM build dir '${C3_RPM_TMPDIR}'"
	-@echo ""
	mkdir -p ${C3_RPM_TMPDIR}/
	mkdir -p ${C3_RPM_TMPDIR}/{SRPMS,RPMS,SOURCES,SPECS,BUILD}			
	mkdir -p ${C3_RPM_TMPDIR}/RPMS/{i386,i586,i686,noarch,athlon,ia64}

# TJN: Remove dirs seperately to try and avoid any errant 'rm -rf' commands.
clean-c3-rpm-tmpdir:
	-@echo ""
	-@echo "Remove temporary RPM build dir '${C3_RPM_TMPDIR}'"
	-@echo ""
	rm -rf  ${C3_RPM_TMPDIR}/RPMS/
	rm -rf  ${C3_RPM_TMPDIR}/SRPMS/
	rm -rf  ${C3_RPM_TMPDIR}/SOURCES/
	rm -rf  ${C3_RPM_TMPDIR}/SPECS/
	rm -rf  ${C3_RPM_TMPDIR}/BUILD/
	rm -rf 	${C3_RPM_TMPDIR}/BUILDROOT/
	rmdir   ${C3_RPM_TMPDIR}/

dist-deb:
	echo "Generating Deb files..."
	@if [ -n "$$UNSIGNED_OSCAR_PKG" ]; then \
        echo "dpkg-buildpackage -rfakeroot -us -uc"; \
        dpkg-buildpackage -rfakeroot -us -uc; \
    else \
        echo "dpkg-buildpackage -rfakeroot"; \
        dpkg-buildpackage -rfakeroot; \
    fi
	@if [ -n "$(PKGDEST)" ]; then \
        mv ../c3*.deb $(PKGDEST); \
    fi
	
deb: dist-deb

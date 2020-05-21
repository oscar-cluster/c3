#!/bin/sh
#
# Copyright (c) 2007-2013 Oak Ridge National Laboratory.  
#                         All rights reserved.
# Copyright (c) 2004-2005 The Trustees of Indiana University and Indiana
#                         University Research and Technology
#                         Corporation.  All rights reserved.
# Copyright (c) 2004-2005 The University of Tennessee and The University
#                         of Tennessee Research Foundation.  All rights
#                         reserved.
# Copyright (c) 2004-2005 High Performance Computing Center Stuttgart, 
#                         University of Stuttgart.  All rights reserved.
# Copyright (c) 2004-2005 The Regents of the University of California.
#                         All rights reserved.
# $COPYRIGHT$
# 
# Additional copyrights may follow
# 
# $HEADER$
#
# TJN: (25jan2011) Adjust to always return at least 3 octets (a.b.c),
#                  even if the 'c' (release) value is zero.
#

srcfile="$1"
option="$2"

case "$option" in
    # svnversion can take a while to run.  If we don't need it, don't run it.
    --major|--minor|--release|--greek|--base|--help)
        C3_NEED_SVN=0
        ;;
    --nightly|*)
        C3_NEED_SVN=1
esac


if test "$srcfile" = ""; then
    option="--help"
else
    C3_MAJOR_VERSION="`cat $srcfile | egrep '^major=' | cut -d= -f2`"
    C3_MINOR_VERSION="`cat $srcfile | egrep '^minor=' | cut -d= -f2`"
    C3_RELEASE_VERSION="`cat $srcfile | egrep '^release=' | cut -d= -f2`"
    C3_GREEK_VERSION="`cat $srcfile | egrep '^greek=' | cut -d= -f2`"
    C3_WANT_SVN="`cat $srcfile | egrep '^want_svn=' | cut -d= -f2`"
    C3_SVN_R="`cat $srcfile | egrep '^svn_r=' | cut -d= -f2`"

	C3_VERSION="$C3_MAJOR_VERSION.$C3_MINOR_VERSION.$C3_RELEASE_VERSION"
	C3_SVN_TAG="c3-$C3_MAJOR_VERSION-$C3_MINOR_VERSION-$C3_RELEASE_VERSION"

     #
     # The Joy of RPM... 
     #  We have to treat the RPM version info specially
     #  as we can not have tilde, etc in the Version: field
     #  So must put that in the Release: field. 
     #  Their use of "Release:" generally means the RPM spec file's
     #  release, but we have to put our GREEK/SVNTAG info there too. 
     #  So we have two special version of version for RPM's two fields.
     #
     #  Note, hardcode all RPM releases to start with "0.1" (just because).
     #
     # See: http://fedoraproject.org/wiki/Packaging:NamingGuidelines
     #
    C3_RPM_VERSION="$C3_MAJOR_VERSION.$C3_MINOR_VERSION.$C3_RELEASE_VERSION"
    C3_RPM_RELEASE="0.1"

     # 
     # The Joy of Debian...
     #  Ok, so Debian wants something similar in that it isolates
     #  the "release"/"epoch" to the right of dash ("-").
     #  So if we had "5.1.3~b1" that would need to be tweaked
     #  to something like 5.1.3-1~b1 (sort of like RPM's 5.1.3-0.1.b1).
     #  Technically, this "5.1.3-1~b1" could change to "5.1.3-2~b1"
     #  if you had a change in just the debian packaging files (not C3 code)
     #  but we maintain it all in the C3 trunk so we'll just blindly
     #  bump the "debian release"/"epoch" and reflect changes elsewhere
     #  in the version (e.g., we'd probably bump that to beta2 "~b2").
     #  I'm adding this comment so I have hope of remembering this in the
     #  future.
     #
     #  Note, hardcode all Debian releases to end with "-1" b/c that
     #  appears to have the best formatting for the way we maintain
     #  the C3 package.
     #
     #  NOTE: I'm tired of this, but it seem sthat the "~b2-1" string,
     #        for example, is actually treated as "~b2" is part of
     #        the package's version, and only the "-1" is the Debian 
     #        packaging release.  But for clarity/simplicity in this
     #        script i'm separating as-is now.  We can adjust in 
     #        the future if '--debrel' is used and results in a problem.
     #
    C3_DEB_VERSION="$C3_MAJOR_VERSION.$C3_MINOR_VERSION.$C3_RELEASE_VERSION"
    C3_DEB_RELEASE=""

    C3_VERSION="${C3_VERSION}${C3_GREEK_VERSION}"

    if test "$C3_GREEK_VERSION" != "0" -a "$C3_GREEK_VERSION" != ""; then
		#
		# XXX: we need tildes "~" in Debian versioning schemes 
		#      for the alpha/beta (greek) field.  For the tags
		#      we'll prune those tildes out to keep svn-tags clean.
		#
		C3_GREEK_VERSION_NOTILDE=`echo $C3_GREEK_VERSION | tr -d -- '~'`
        C3_SVN_TAG="$C3_SVN_TAG-$C3_GREEK_VERSION_NOTILDE"

        # 
        # XXX: Append this alpha/beta (greek) field to RPM "Release:"
        #      (because we can NOT include it in the RPM "Version:")
        #
        C3_RPM_RELEASE="$C3_RPM_RELEASE.$C3_GREEK_VERSION_NOTILDE"

        # 
        # XXX: Append the alpha/beta (greek) field to Debian "release"
        #    (we CAN have tilde w/ Deb but keeping it consistent with RPM case)
        #
        C3_DEB_RELEASE="${C3_DEB_RELEASE}${C3_GREEK_VERSION}"
    fi

    C3_BASE_VERSION="$C3_VERSION"

    C3_DATE=`date '+%Y%m%d'`

    if test "$C3_WANT_SVN" = "1" -a "$C3_NEED_SVN" = "1" ; then
        if test "$C3_SVN_R" = "-1"; then
            if test -d .svn; then
                ver="r`svnversion .`"
            else
                ver="svn`date '+%m%d%Y'`"
            fi
            C3_SVN_R="$ver"
        fi
        C3_VERSION="${C3_VERSION}$C3_SVN_R"
   
        C3_RPM_RELEASE="${C3_RPM_RELEASE}${C3_SVN_R}"
        C3_DEB_RELEASE="${C3_DEB_RELEASE}${C3_SVN_R}"
    fi

     #  Note, hardcode all Debian releases to start with "1" (just because).
     #        Always add as trailing "-1" to our debian releases.
    C3_DEB_RELEASE="${C3_DEB_RELEASE}-1"

    C3_RPM_FULL_VERSION="${C3_RPM_VERSION}-${C3_RPM_RELEASE}"
    C3_DEB_FULL_VERSION="${C3_DEB_VERSION}${C3_DEB_RELEASE}"

    if test "$option" = ""; then
	option="--full"
    fi
fi

case "$option" in
    --full|-v|--version)
	echo $C3_VERSION
	;;
    --major)
	echo $C3_MAJOR_VERSION
	;;
    --minor)
	echo $C3_MINOR_VERSION
	;;
    --release)
	echo $C3_RELEASE_VERSION
	;;
    --greek)
	echo $C3_GREEK_VERSION
	;;
    --svn)
	echo $C3_SVN_R
	;;
    --svn-tag)
	echo ${C3_SVN_TAG}
	;;
    --rpmfull)
	echo ${C3_RPM_FULL_VERSION}
	;;
    --rpmver)
	echo ${C3_RPM_VERSION}
	;;
    --rpmrel)
	echo ${C3_RPM_RELEASE}
	;;
    --debfull)
	echo ${C3_DEB_FULL_VERSION}
	;;
    --debver)
	echo ${C3_DEB_VERSION}
	;;
    --debrel)
	echo ${C3_DEB_RELEASE}
	;;
    --base)
        echo $C3_BASE_VERSION
        ;;
    --all)
        echo ${C3_VERSION} ${C3_MAJOR_VERSION} ${C3_MINOR_VERSION} ${C3_RELEASE_VERSION} ${C3_GREEK_VERSION} ${C3_SVN_R}
        ;;
    --nightly)
	echo ${C3_VERSION}nightly-${C3_DATE}
	;;
    -h|--help)
	cat <<EOF
$0 <srcfile> [<option>]

<srcfile> - Text version file
<option>  - One of:
    --full    - Full version number
    --major   - Major version number
    --minor   - Minor version number
    --release - Release version number
    --greek   - Greek (alpha, beta, etc) version number
    --svn     - Subversion repository number
    --svn-tag - Subversion tagging string (C3 release tags)
    --rpmfull - Full RPM Version number (proper format for version/release)
    --rpmver  - RPM Version number (RPM compatible format for 'Version:')
    --rpmrel  - RPM Release number (RPM compatible format for 'Release:') 
    --debver  - Full Debian Version number (proper format for version/release)
    --debver  - Debian Version number (Debian compatible format for version)
    --debrel  - Debian Version number (Debian compatible format for release)
    --all     - Show all version numbers, separated by :
    --base    - Show base version number (no svn number)
    --nightly - Return the version number for nightly tarballs
    --help    - This message
EOF
        ;;
    *)
        echo "Unrecognized option $option.  Run $0 --help for options"
        ;;
esac

# All done

exit 0

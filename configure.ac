
dnl ===================== C3 Configure Script ======================

AC_INIT([c3], m4_esyscmd([./dist/get-version.sh ./VERSION --full | tr -d '\n']))
AC_CONFIG_SRCDIR([src/cexec])
AM_INIT_AUTOMAKE

dnl ================== Check if python is installed ==================

AM_PATH_PYTHON([2.4])

dnl ==================================================================

AC_OUTPUT(Makefile)


dnl ============ Generate top-level C3-VERSION file ==================

m4_esyscmd([./dist/get-version.sh ./VERSION --full > C3-VERSION])



dnl ============ Substitution into related .in file(s) ===============

dnl == All below example assume a VERSION file of "c3-5.1.3~b1" ==

dnl == Example: "5.1.3~b1" ==
AC_SUBST([C3_VERSION], 
         m4_esyscmd([./dist/get-version.sh ./VERSION --full]))

dnl == Example: "5" ==
AC_SUBST([C3_VERSION_MAJOR], 
          m4_esyscmd([./dist/get-version.sh ./VERSION --major]))

dnl == Example: "/opt/c3-$C3_VERSION_MAJOR" ==
AC_PREFIX_DEFAULT(m4_join([-], 
               [/opt/c3],
               m4_normalize(esyscmd(./dist/get-version.sh ./VERSION --major))))

dnl == Example: "5.1.3" ==
dnl == See comments in get-version.sh ==
AC_SUBST([C3_RPM_VERSION], 
         m4_esyscmd([./dist/get-version.sh ./VERSION --rpmver]))

dnl == Example: "0.1.b3" ==
dnl == See comments in get-version.sh ==
AC_SUBST([C3_RPM_RELEASE], 
         m4_esyscmd([./dist/get-version.sh ./VERSION --rpmrel]))

AC_CONFIG_FILES([src/ckillnode], [chmod +x src/ckillnode])
AC_CONFIG_FILES([rpm/c3.spec],   [chmod +r rpm/c3.spec])
AC_CONFIG_FILES([src/c3.csh],    [chmod +x src/c3.csh])
AC_CONFIG_FILES([src/c3.sh],     [chmod +x src/c3.sh])
AC_CONFIG_FILES([src/c3_version.py])

AC_OUTPUT


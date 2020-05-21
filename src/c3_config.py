# $Id: c3_config.py 186 2011-01-21 23:07:00Z tjn $

import os
import os.path
import c3_version

#This file holds all the variables used by the other utilities

C3_OKEXIT = 0
C3_ERRLOCAL = 1
C3_ERRREMOTE = 2
def_path = ''

try:
	def_path = os.environ[ 'C3_PATH' ]
except KeyError:
	if os.path.isfile('/usr/bin/cexec') and os.access('/usr/bin/cexec', os.X_OK):
		def_path = '/usr/bin'
	else:
		def_path = '/opt/c3-' + `c3_version.c3_version_major`

# vim:tabstop=4:shiftwidth=4:noexpandtab:textwidth=76

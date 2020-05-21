# $Id: c3_except.py 186 2011-01-21 23:07:00Z tjn $

class c3_except:
	description = ""
	last = ""

	def __init__(self, string, name):
		self.description = string
		self.last = name


class parse_error( c3_except ):
	pass

class bad_cluster_name( parse_error ):
	pass

class no_more_clusters( c3_except ):
	pass

class invalid_head_node( parse_error ):
	pass

class invalid_cluster_block( parse_error ):
	pass

class no_head_node( c3_except ):
	pass

class invalid_node( parse_error ):
	pass

class end_of_cluster( c3_except ):
	pass

class internel_error( c3_except ):
	pass

class indirect_cluster( parse_error ):
	pass

class not_in_range( parse_error ):
	pass

class end_of_option( c3_except ):
	pass

class bad_string( parse_error ):
	pass

class end_of_opt_string( bad_string ):
	pass

# vim:tabstop=4:shiftwidth=4:noexpandtab:textwidth=76

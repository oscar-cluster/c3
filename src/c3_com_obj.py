# $Id: c3_com_obj.py 186 2011-01-21 23:07:00Z tjn $

import re, sys
from c3_except import *

# class used to represent cluster taken from command line
# clusters is the list of cluster names used as a key in the
# nodes associative array. To iterate through them would look as such:
# for cname in c3_cluster_list.clusters:
#	for node in c3_cluster_list[cname]:
#		print node

class c3_cluster_list:
	def __init__(self):
		self.clusters = []
		self.node = {}
		self.username = {}
class c3_command_line:


	# matches any non whitespace word
        any_token = re.compile( r"\s*(?P<word>\S+)" )

	# matches a - or -- and then the option name
	option = re.compile( r"\s*(?P<word>--?\w+)" )
	
	# matches a cluster name
	c_name = re.compile( r"\s+(?P<username>[\w_\-]+@)?(?P<name>[\w_\-]+)?:" );
	
	# matches a single number
	number = re.compile( r"\s*(?P<num>\d+)" );
	
	# matches a range quaifier "-"
	range_qual = re.compile( r"\s*-" );
	
	# matches a single node qualifier ","
	single = re.compile( r"\s*," );
 
	# initiliaze line as an enpty string
	line = ""


	# initilaize internal line as the text to be parsed
	def __init__( self, command_line ):
		self.line = command_line

	# returns a single option, a - or -- followed by string
	def get_opt( self ):
		match = self.option.match( self.line )
		if match:
			line_out = ""
			line_out = match.group( "word" )
			self.line = self.line[match.end():]
		else:
			raise end_of_option( None, None )
		return line_out

	# returns a single token, used for cases such as --file FILENAME to get FILENAME
	def get_opt_string( self ):
		match = self.any_token.match( self.line )
		if match:
			line_out = ""
			line_out = match.group( "word" )
			self.line = self.line[match.end():]
		elif len( self.line ) == 0:
			raise end_of_opt_string( "option needs a string", None)
		else:
			raise bad_string( "option requires a string", None )
		return line_out

	# all parsing is done externally through this command
	def get_clusters( self ):
		cluster_obj = c3_cluster_list()

		# check if any clusters are specified on the command line, if not
		# then set execution to default cluster (name not known at this point
		# /default is an invalid cluster name and hence a place holder in this
		# context
		match = self.c_name.match( self.line )
		if not match:
			cluster_obj.clusters.append( "/default" )
			cluster_obj.node["/default"]=[]
			cluster_obj.node["/default"].append( "" )
			cluster_obj.username["/default"]="/default"
		# while there are still cluster blocks on the command line
		while match:
			# string parsed text from line
			self.line = self.line[match.end():]
			# if a name is specified get it, else : is specified set to default cluster
			if match.group( "name" ):
				index = match.group( "name" )
			else:
				index = "/default"

			#if an alternate username is specified use it.
			if match.group( "username" ):
				cluster_obj.username[index]=match.group( "username" )[:-1]
			else:
				cluster_obj.username[index]="/default"

			# add name to cluster list and initialize node list	
			cluster_obj.clusters.append( index )

			match = self.number.match( self.line )
			cluster_obj.node[index] = []
			cluster_obj.node[index].append( "" )
			node_index = 0
			
			# if a range has been specified on command line parse it
			# this process gets the first number from the list and stores it in a temp
			# var. Then checks if it is part of a range or a single number. If it is a range 
			# it processes once and then checks for a single number, if it is a single number
			# it processes single numbers until wither the end of the node position specification
			# or a range qualifier is found, if a range is found the process loops. In this way the 
			# would be parsed correctly: "1,3,4-8,10-20,25"
			while match:
				# strip parsed text from line
				self.line = self.line[match.end():]
				# get starting number from match
				cluster_obj.node[index][node_index] = int( match.group( "num") )
				# if a match is specified parse it
				match = self.range_qual.match( self.line )
				if match:
					# strip parsed text from line
					self.line = self.line[match.end():]
					match = self.number.match( self.line )
					# set start and end of range
					start_range = cluster_obj.node[index][node_index] + 1
					if match:
						end_range = int( match.group( "num" ) ) + 1
					else:
						self.line = '-' + self.line
						return cluster_obj
					# loop from start to end and add node position to node list
					for counter in  range( start_range, end_range ):
						node_index = node_index + 1
						cluster_obj.node[index].append( "" )
						cluster_obj.node[index][node_index] = counter
					# strip parsed text from line
					self.line = self.line[match.end():]
				# check for single numbers (2,5,6)
				match = self.single.match( self.line )
				if match:
					# srip parsed text from line
					self.line = self.line[match.end():]
					# add node poistion to node list
					cluster_obj.node[index].append( "" )
					node_index = node_index + 1
					match = self.number.match( self.line )
			match = self.c_name.match( self.line )
		try:
			if self.line[0] != ' ':
				raise bad_cluster_name ( None, None )
		except IndexError:
			pass
		return cluster_obj

	# returns the rest of line (usually for the end of the command)
	def rest_of_command( self ):
		return self.line	

# vim:tabstop=4:shiftwidth=4:noexpandtab:textwidth=76

# $Id: c3_file_obj.py 186 2011-01-21 23:07:00Z tjn $

import sys, re
from c3_except import *

# this is the internal representation of a node
# as of right now it is just simply it's name
# (ip or alias) and it's status. dead = 0 is alive
# dead = 1 id offline
class node_obj:
	name = ""
	dead = 0

class cluster_def:
	"parses the cluster definition file"

	###################################################################
	#  this is the regular expressions used parse the file            #
	###################################################################
	
	# beginning of cluster definition (name of the cluster)
	# matches cluster_name {
	cluster_name = re.compile ( r"""
		\s*cluster\s+		#cluster keyword
		(?P<c_name>		#cluster name
			[\w_\-]+	#may contain an alphanumeric, underscore, and dash
		)\s*{[\t\v ]*(\#.*)?\n""", re.VERBOSE | re.IGNORECASE
	)

	# extracts the name of the head node
	# matches external:internal 
	# with the internal name optional
	head_node = re.compile ( r"""
		\s*			#get rid of whitespace
		(?P<extname>		#external head node name goes first
			[\w\-\.]+
		)?
		(:			#if internal name spcified
			(?P<intname>	#extract internal name
				[\w\-\.]+
			)
		){0,1}[\t\v" "]*(\#.*)?\n""", re.VERBOSE
	)

	# extracts the name of compute nodes
	# matches dead nodename 
	# with dead being optional and including
	# ranges
	compute_node = re.compile ( r"""
		\s*	#get rid of whitespace
		(?P<dead_node>
			dead[\t\v" "]+
		)?
		(?P<comname>	#get name of current node
			[\w\-.]+		#non range part of name
		)
		(?P<range>
			\[(?P<start>\d+)\-(?P<stop>\d+)\]	#get range (optional)
		){0,1}[\t\v" "]*(\#.*)?\n""", re.VERBOSE
	)


	# exclude nodes from a range
	# matches exclude [num1-num2]
	# with num1 and num2 being integers
	exclude = re.compile ( r"""
		\s*exclude\s*
		((?P<single>\s+\d+)|(\[(?P<start>\d+)\-(?P<stop>\d+)\]))
		[\t\v" "]*(\#.*)?\n
		""", re.VERBOSE | re.IGNORECASE
	)

	# matches brackets { }
	start_bracket = re.compile( """\s*{""" )
	end_bracket = re.compile ( """\s*}[\t\v" "]*""" )

	# matches any non whitespace character
	any_token = re.compile ("\s*\S+")

	# matches a comment line
	comment = re.compile( r"[ \t\r\f\v]*#.*\n" )

	#########################################################
	# variables needed for execution			#
	#########################################################

	# filename of cluster config file
	file = ""

	# this is a string used to hold the config file
	line = ""

	# string to hole the current cluster name
	c_name = ""
	
	#strings to hold the head node names
	head_int = ""
	head_ext = ""

	#list to hold ranges for nodes
	node_list = []

	#used to show place where error occured
	last_cluster = "first cluster in list"
	last_machine = "first node in list"

	#########################################################
	#							#
	# this is the constructor, it takes the filename of the #
	# config file to parse, the second init throws an error #
	# if no file name is given				#
	#							#
        #########################################################
	def __init__(self, filename):

		self.file = filename
		inputfile = open( filename, "r" )

		# generate a string containing the file 
		line_in = inputfile.readline()
		while line_in:
			self.line = self.line + line_in
			line_in = inputfile.readline()
		inputfile.close()

	#########################################################
	# resets the internal variables after an error		#
	#########################################################
	def reset_vars(self):
		self.line	= 	""
		self.c_name 	= 	""
		self.head_int	=	""
		self.head_ext	=	""
		self.node_list	=	[]
		self.last_cluster = 	"first cluster in list"
		self.last_machine = 	"first node in list"

	#########################################################
	# re-initializes the file (begins at the first cluster  #
	# again)						#
	#########################################################
	def reread_file(self):
		self.reset_vars()
		self.__init__(self.file)

	#########################################################
	# strips comments from front of file			#
	#########################################################
	def strip_comments( self ):
	
		match = self.comment.match( self.line )
		while match:
			self.line = self.line[match.end():]
			match = self.comment.match( self.line )

	#########################################################
	# scans to next cluster in the file, if called for the  #
	# first time goes to first cluster			#
	# doesn't return anything, just sets internal variable	#
 	#########################################################
	def get_next_cluster(self):

		self.strip_comments()
		match = None

		try:
			while not match:  #loop untill a cluster tag is found
				match = self.cluster_name.match( self.line )
			        if match: #if cluster tag found
					# get cluster name
					self.c_name = match.group( "c_name" )
					self.line = self.line[match.end():]
					self.strip_comments()
					self.last_cluster = self.c_name 
			        	try:
						match = self.head_node.match( self.line )
				        	if not match.group( "extname" ):
							# this indicates that it is an "indirect" cluster
							# the internal node is actually the external link
							# it was done this way because with normal operation
							# this would be an impossible state 
							self.head_ext = None
							self.head_int = match.group( "intname" )
						else: # "direct" cluster
							self.head_ext = match.group( "extname" )
							self.head_int = match.group( "intname" )
							if not self.head_int:
								self.head_int = self.head_ext
					except AttributeError: # parse error on the head node
						name = self.c_name
						self.reset_vars()
						raise invalid_head_node( "invalid head node specification", name)
				       	self.line = self.line[match.end():]
					self.strip_comments()
				else: # cluster tag not found
					# strip a single token from self.line
					match = self.any_token.match( self.line );
					# an open bracket here would mean that a valid cluster tag was not found
					# but a new cluster block was trying to be formed
					if self.start_bracket.match( match.group() ):
						name = self.last_cluster
						self.reset_vars()
						raise invalid_cluster_block( "invalid cluster definition", name)
					self.line = self.line[match.end():]
					self.strip_comments()
					match=None
		except AttributeError: # invalid cluster definition
			name = self.last_cluster
			self.reset_vars()
			raise no_more_clusters( "No more valid cluster blocks", name )

	#########################################################
	# returns the external name of the current cluster 	#
	# being parsed						#
	#########################################################
	def get_external_head_node(self):
		if self.head_ext == "":
			raise no_head_node( "no head node set.", "no cluster read yet." )
		return self.head_ext;
	
	#########################################################
	# returns the internal name of the current cluster 	#
	# being parsed						#
	#########################################################
	def get_internal_head_node(self):
		if self.head_int == "":
			raise no_head_node( "no head node set.", "no cluster read yet." )
		return self.head_int;

	#########################################################
	# returns the name of the next node in the files if 	#
	# called for the first time returns the first node name #
	# returns a node_obj with the appropriate values filed	#
	# in							#
	#########################################################
	def get_next_node(self):
		
		self.strip_comments()

		# the only time it is possible for this to occur is
		# with indirect clusters
		if self.head_ext == None:
			name = "cluster " + self.c_name
			raise indirect_cluster( "indirect clusters don't have nodes", name )
		
		node_out = node_obj()

		# when a range is specified a queue is built with the nodes
		# so if a queue is present then we know that a range has
		# been specified and must be used up before we parse another
		# line in the file
		if self.node_list:
			node_out = self.node_list.pop(0)
			self.last_machine = node_out.name
			return node_out

		match = self.compute_node.match( self.line )
 
	        if match: # if a compute node is found

			self.line = self.line[match.end():]
			self.strip_comments()
               		if match.group( "dead_node" ): # check if it is a dead node 
	                        if not match.group( "range" ): # dead node qualifier invalid with a range
               		        	node_out.name = match.group( "comname" )
					node_out.dead = 1        
	                        else: # return the given node with a dead set to true
					name = self.last_machine + " in " + self.c_name
					self.reset_vars()
					raise invalid_node( "dead specifier can not have a range", name )
	                else: # either a range or single node specified
               		        if match.group( "range" ): # if range
					# retrieve starting and stopping ranges
               		                start_add_range = int( match.group( "start" ) )
					stop_add_range = int( match.group( "stop" ) ) + 1
					# start is always zero - start_add_range - start_add_range
					# this is done so that the indexing starts at zero
					start = 0
					stop = stop_add_range - start_add_range
					for index in range(start, stop): # populate list
						self.node_list.append( node_obj() )
						self.node_list[index].name = match.group( "comname" ) + str( index + start_add_range )
						self.node_list[index].dead = 0
					match = self.exclude.match( self.line )
					# multiple exclude lines after a range are valid, hence the while loop
	        		        while match and self.node_list: 
	                			try:
							if match.group( "single" ): # excluding a single machine
								index = int( match.group( "single" ) ) 
								if index < 0:
									raise IndexError
								self.node_list[index - start_add_range].dead = 1
							else: # excluding a range
								start_ex_range = int( match.group( "start" ) )
								stop_ex_range = int( match.group( "stop" ) )
								# list index starts at zero so the exclude index and
								# list index must co-incide
								start = start_ex_range - start_add_range
								stop = (stop_ex_range - start_add_range) + 1
								if (start <  0) or (start > stop):
									raise IndexError
								for index in range (start, stop):
									self.node_list[index].dead = 1
							self.line = self.line[match.end():]
							self.strip_comments()
							match = self.exclude.match( self.line) # check for second exclude
						except IndexError:
							name = self.last_machine + " in " + self.c_name
							raise not_in_range( "index in exclude is not in range", name)

					node_out = self.node_list.pop(0)
				else: # single node specifier 
					node_out.name = match.group( "comname" )
					node_out.dead = 0	
	               
               		
		else: # either there are no more nodes ( closing bracket is found )
		      # or there was a parse error on the node specification line
			if self.end_bracket.match( self.any_token.match(self.line).group() ):
				raise end_of_cluster( "no more nodes in config file", None )
			name = self.last_machine + " in " + self.c_name
			self.reset_vars()
			raise invalid_node( "invalid specification for a node", name )
		self.last_machine = node_out.name
		return node_out

	#########################################################
	# returns the name of the current cluster being read    #
	#########################################################
	def get_cluster_name(self):
		if self.c_name == "":
			raise no_cluster_name( "read in a cluster before useing", "no cluster read yet" )
		return self.c_name

# vim:tabstop=4:shiftwidth=4:noexpandtab:textwidth=76

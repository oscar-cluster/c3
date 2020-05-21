# $Id: c3_sock.py 209 2011-02-02 23:38:27Z tjn $

import os, sys, time
from select import select
from subprocess import *

# this class is used so that I can use strong authentication without
# much hassel and easily implement timeouts. As I am only sending a frame or
# two at a time it is not really noticable. This also allows an abstraction layer 
# so that I can later change to raw socets/PVM/ or whatever without a major code
# re-write: in no way is this meant for speed :)

# one thing to note: these differ from real sockets API in one major way. since the server 
# uses popen to initiate a connextion the clients stdin/stdout is mapped as the socket, thus
# once a client sock has been established all prints will also go to the server, thus you could
# really mess up communications by doing this - be carefull if you use them.

class c3_sock:
	# I use these to abstract whether or not I am writing to stdout/stdin (client)
	# or a pipe (server)
	output_pipe = None
	input_pipe = None
	# default timeout of 10 seconds
	timeout = 10

	# self explanitory
	def set_timeout( self, new_timeout ):
		self.timeout = new_timeout
		
	# general form if a messsage is length:message
	# Simply pack the message and write to a pipe
	def send( self, string_to_send  ):
		length = len( string_to_send )
		string_to_send = str(length) + ':' + string_to_send
		self.output_pipe.write( string_to_send )
		self.output_pipe.flush()


	# these sockets timeout on a receive (think of this as more along the
	# lines of UDP instead of TCP). Thus if you have a client that will sit 
	# a while processing you need some form of stayalive message (I dont
	# do anything that complicated in C3 so I didn't implement them)
	def recieve( self ):
		buffer = ""
		# read a single character in until you get the size terminator
		char_in = self.input_pipe.read( 1 )
		time_start = time.time()
		time_elapsed = 0
		while char_in != ':':
			buffer = buffer + char_in
			char_in = self.input_pipe.read( 1 )
			# as you can see timeouts work but are kinda cheesy, use a nonblocking
			# read and increment a time counter if nothing is retuned, raise and exception
			# if a threshold is crosed.
			time_elapsed = time.time() - time_start
			if char_in != "":
				time_start = time.time()
			if char_in == "" and time_elapsed > self.timeout:
				raise 'time_out'

		# try and read the message from the pipe in as large a chunk as possible, loop
		# untill stated length is reached
		length = int (buffer)
		buffer = self.input_pipe.read( length )
		time_start = time.time()
		time_elapsed = 0
		while len(buffer) < length:
			new_buffer = buffer + self.input_pipe.read( length )
			if len(new_buffer) > len(buffer):
				time_start = time.time()
				time_elapsed = 0
				buffer = new_buffer
			elif time_elapsed > self.timeout:
				raise 'time_out'
			else:
				time_elapsed = time.time() - time_start
		# return message received through pipe		
		return buffer

	def close( self ):
		self.__del__()

# server sock just defines two pipes (input, output) and initializes a command
# this this socket is a socket to a command. Think "ssh node10 client_code"
# where client code communicates through stdin and stdout.
# when it's done simply close pipes
class server_sock( c3_sock ):

	def __init__(self, command):
		#self.output_pipe, self.input_pipe = os.popen2( command )
		# XXX: Changed to subprocess module (see ticket:16)
		p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
		(self.output_pipe, self.input_pipe) = (p.stdin, p.stdout)



	def __del__( self ):
		self.output_pipe.close()
		self.input_pipe.close()
		
# the client sock takes stdin/stdout and map them to another pipe, this is so
# the same send/receive function can be used. Since the socket uses only
# stdin/stdout to communicate only one socket can be running at a time per
# instance of the PROGRAM. stdout and stdin are set to None to catch this error.
# on socket closing stdin and stdout are set back to thier original values.
class client_sock( c3_sock ):

	def __init__(self):
		if sys.stdout == None and sys.stdin == None:
			raise 'single client only'
		self.output_pipe = sys.stdout
		self.input_pipe = sys.stdin
		sys.stdout = None
		sys.stdin = None



	def __del__( self ):
		sys.stdin = self.input_pipe
		sys.stdout = self.output_pipe

# vim:tabstop=4:shiftwidth=4:noexpandtab:textwidth=76

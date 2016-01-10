#!/usr/bin/env python
import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time

user_list = []
session_list = []

def acceptUser(data): #user accepted to server for the first time(user login)
	if data[0:3] == "USR":
			if data[4:] not in user_list:
				user_list.append(data[4:])
				response = "HEL " + data[4:] #user nickname accepted
				 
			else:
				response = "REJ" #nickname exists
	else:
		response = "ERL" #wrong user login command
	return response


class ReadThread (threading.Thread):
	def __init__(self, readThreadID, csoc):
		threading.Thread.__init__(self)
		self.readThreadID = readThreadID
		self.csoc = csoc
		self.nickname = ""

	def incoming_parser(self, data):

                if len(data) > 3 and not data[3] == " ":
			response = "ERR"

		if len(request) == 0:
			return
                
		requestWithParam = data.split()
		request = cmdWithParam[0][1:]
		if len(cmdWithParam) > 1:
                        parameter = cmdWithParam[1]

                elif request[0:3] == 'TIC':
			response = 'TOC'		

                elif request[0:3] == "USR": #user changes nickname
			if parameter not in user_list:
				if(self.nickname in user_list):
					user_list.remove(self.nickname)
				user_list.append(parameter)
				response = "HEL " + parameter
				self.nickname = parameter
				 
			else:
				response = "REJ"
		
		elif request[0:3] == "QUI":
			response = "BYE " + self.nickname
			self.csoc.send(response)
			user_list.remove(self.nickname)
##			threadList.remove(self.readThreadID)
			return

		elif request[0:3] == "LSQ":
			response = "LSA " + ":".join(user_list)

		elif request[0:3] == "LUQ":
			response = "LUA " + ":".join(session_list)
	
		elif request[0:3] == "JOS":
			response = "JOK"

		elif request[0:3] == "NES":
                        if parameter not in session_list:
				session_list.append(parameter)
				response = "SOK"
                        else:
				response = "SER"

		elif request[0:3] == "RDY":
			response = "NEW"

		elif request[0:3] == "NXT":
			response = "NUM"

		elif request[0:3] == "CNK":
			response = "COK/CER"
			
		elif request[0:3] == "TOM":
			response = "TOK/TER"
			
		elif request[0:3] == "FIN":
                        #herkes goruntulediyse
##                        session_list.remove(parameter)
                        
			response = "END"

		else:
			response = "ERR"
		
		print "response: "
		print response
		self.csoc.send(response)
		return 

	def run(self):
		while True: #for default client commands
			data = self.csoc.recv(1024)
			print data
			self.incoming_parser(data) 
			



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()

port = 12345
s.bind((host,port))

readThreadID = 1;
threadList = []
while True:
	s.listen(5)
	c, addr = s.accept()
	print 'Got connection from', addr
	thread = ReadThread(readThreadID, c)
	thread.start()
	threadList.append(readThreadID)
	readThreadID += 1









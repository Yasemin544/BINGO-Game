#!/usr/bin/env python
import sys
import socket
import threading
import Queue
import time
import random

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

                response = 'ERR'
                if len(data) > 3 and not data[3] == " ":
			response = 'ERR'

		if len(data) == 0:
			return
                
		requestWithParam = data.split()
		request = requestWithParam[0]
		
		if len(requestWithParam) > 1:
                        parameter = requestWithParam[1]

                if request[0:3] == 'TIC':
			response = 'TOC'		
               
                elif request[0:3] == 'USR': #user changes nickname
			if parameter not in user_list:
				if(self.nickname in user_list):
					user_list.remove(self.nickname)
				user_list.append(parameter)
				response = 'HEL ' + parameter
				self.nickname = parameter
				 
			else:
				response = 'REJ'
		
		elif request[0:3] == 'QUI':
			response = 'BYE ' + self.nickname
			self.csoc.send(response)
			user_list.remove(self.nickname)
##			threadList.remove(self.readThreadID)
			return

		elif request[0:3] == 'LSQ':
			response = 'LSA ' + ":".join(user_list)

		elif request[0:3] == 'LUQ':
			response = 'LUA ' + ":".join(session_list)
	
		elif request[0:3] == 'JOS':
			response = 'JOK'

		elif request[0:3] == 'NES':
                        if parameter not in session_list:
				session_list.append(parameter)
				response = 'SOK'
                        else:
				response = 'SER'

		elif request[0:3] == 'RDY':
                        user_count = len(user_list)
                        cards = []
                        for i in range(user_count):
                                card = random.sample(range(1,90), 15)
                                cards.append(card)
                        print cards
                        
			response = 'NEW ' + str(cards[0])
			print response

		elif request[0:3] == 'NXT':
			response = 'NUM'

		elif request[0:3] == 'CNK':
			response = 'COK/CER'
			
		elif request[0:3] == 'TOM':
			response = 'TOK/TER'
			
		elif request[0:3] == 'FIN':
                        #herkes goruntulediyse
##                        session_list.remove(parameter)
                        
			response = 'END'

		else:
			response = 'ERR'
		
				
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









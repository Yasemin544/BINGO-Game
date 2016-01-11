#!/usr/bin/env python
# user_info = {'183.654.25.21': {nick: 'nick'  session: 'session'}}
# session_info = {'pros': {users: [csoc1, csoc2], cards: [], random_num : [] }  , 'newbies' : [csoc3]}
import sys
import socket
import threading
import Queue
import time
import random

user_info = {}
session_info = {}

def acceptUser(data, csoc): #user accepted to server for the first time(user login)
	if len(data) > 4:
		parameter = data[4:]
	if data[0:3] == "USR":
			if parameter not in user_info:
				user_info[csoc]['nick'] = parameter
				user_info[csoc]['session'] = ''
				response = "HEL " +parameter #user nickname accepted
				 
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
		self.session = ""

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
                       
                elif request[0:3] == 'USR':
                        if parameter not in user_info:
                                if(self.nickname in user_info):
                                        del user_info[self.nickname]  #user changes nickname
                                user_info[csoc]['nick'] = parameter
                                user_info[csoc]['session'] = ''
                                response = 'HEL ' + parameter
                                self.nickname = parameter
                        else:
                                response = 'REJ'
                        
                elif request[0:3] == 'QUI':
                        response = 'BYE ' + self.nickname
                        self.csoc.send(response)
                        del user_info[self.nickname]
        ##		threadList.remove(self.readThreadID)
                        return

                elif request[0:3] == 'LSQ':
                        
                        response = 'LSA ' + ",".join(session_info.keys())

                elif request[0:3] == 'LUQ':
                        if self.session == "":
                                response = "LNA" #"You cannot list users before you login a session."

                        else:
                                user_list = self.get_users_of_session()
                                response = 'LUA ' + ",".join(user_list)

                elif request[0:3] == 'JOS':
                        if parameter in session_info:
                                if len(session_info[parameter]) < 3:
                                        session_info[parameter]['users'][self.csoc] = ''
                                        user_info[csoc]['session'] = parameter
                                        self.session = parameter
                                                                                
                                        print "ses"
                                        print session_info
                                        print "user"
                                        print user_info
                                        response = "JOK"
                                else:
                                        response = "FUL"
                        else:
                                response = "JER"

                elif request[0:3] == 'NES':
                        if parameter in session_info:
                                response = "SER"
                        else:
                                session_info[parameter] = {}
                                session_info[parameter]['users'] = {}
                                session_info[parameter]['users'][self.csoc] = ''#initial state
                                session_info[parameter]['random_numbers'] = random.sample(range(1, 91), 90)
                                user_info[csoc]['session'] = parameter
                                print session_info
                                self.session = parameter
                                response = "SOK"
                                
                elif request[0:3] == 'RDY':
                        print "session_info", session_info
                        print "user info", user_info
                        print "user in sesion", session_info[self.session]['users']
                        while True:
                                user_count = len(session_info[self.session]['users'])
                                if user_count == 3: 
                                        break
                        #user_count = len(session_info[session])
                        session_info['cards'] = random.sample(range(1, 91), 90)
                        if user_count == 3:
                                cards = []
                                for i in range(user_count):
                                        card = random.sample(range(1,91), 15)
                                        cards.append(card)
                                print cards
                                session_info[self.session]['cards'] = cards
                                                        
                                response = 'NEW ' + str(cards[0])
                                print response

                elif request[0:3] == 'NXT':
                        session_info[session][csoc] = '1'
                        ready_count = session_info[session].values().count('1')
                        user_count = len(session_info[session])
                        if ready_count == user_count:
                                next_number = session_info['random_numbers'].pop()
                                response = "NEW ", next_number
                                #send to all clients:
                                broadcast_response(self.session, response)
                                key = session_info[session].keys()
                                for key in keys:
                                        session_info[session][key] = '0'
                                return
                                        
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
                        
                print response         
                self.csoc.send(response)
                return 
		
        def get_users_of_session(self):
		client_list = session_info[self.session].keys()
		user_list = []
		for client in client_list:
			user_list.append(user_info[client]['nick'])
                return user_list
		
	def run(self):
		while True: #for default client commands
                        data = self.csoc.recv(1024)
			print data
			self.incoming_parser(data) 
			

def broadcast_response(session, response):
	clients = session_info[session].keys()
	for client in clients :
		client.send(response)
	
	

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()

port = 12345
s.bind((host,port))

readThreadID = 1;
threadList = []
while True:
	s.listen(5)
	csoc, addr = s.accept()
	user_info[csoc] = {}
	print 'Got connection from', addr
	thread = ReadThread(readThreadID, csoc)
	thread.start()
	threadList.append(readThreadID)
	readThreadID += 1
	#thread.join()


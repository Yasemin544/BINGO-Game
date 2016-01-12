#!/usr/bin/env python
# user_info = {socketobj: {'nick': nickname , 'session': sessionname}}
# session_info = {sessionname: {'cards': [[]], 'random_numbers': [], 'past_numbers': [],  'users': {socketobj: {'state': '', cinko_rows: []}}
import sys
import socket
import threading
import Queue
import time
import random
import ast
import re
from collections import OrderedDict

user_info = {}
session_info = {}
MAX_USER = 2 #number of users in a session

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
                                user_info[self.csoc]['nick'] = parameter
                                user_info[self.csoc]['session'] = ''
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
                                user_list = self.getUsersofSession()
                                response = 'LUA ' + ",".join(user_list)

                elif request[0:3] == 'JOS':
                        if parameter in session_info:
                                if len(session_info[parameter]['users']) < MAX_USER:   #save session info
                                        session_info[parameter]['users'][self.csoc] = {}
                                        session_info[parameter]['users'][self.csoc]['state'] = '' #initial state
                                        session_info[parameter]['users'][self.csoc]['cinko_rows'] = []
                                        user_info[self.csoc]['session'] = parameter
                                        self.session = parameter
                                        response = "JOK"
                                else:
                                        response = "FUL" #session is full
                        else:
                                response = "JER"

                elif request[0:3] == 'NES':
                        if parameter in session_info:
                                response = "SER"
                        else:
                                session_info[parameter] = {}
                                session_info[parameter]['users'] = {}
                                session_info[parameter]['users'][self.csoc] = {}
                                session_info[parameter]['users'][self.csoc]['state'] = '' 
                                session_info[parameter]['users'][self.csoc]['cinko_rows'] = []
                                session_info[parameter]['random_numbers'] = random.sample(range(1, 91), 90)
                                user_info[self.csoc]['session'] = parameter
                                self.session = parameter
                                response = "SOK"
                                
                elif request[0:3] == 'RDY':
                        while True:
                                user_count = len(session_info[self.session]['users'])
                                if user_count == MAX_USER: 
                                        break
                        session_info[self.session]['random_numbers'] = random.sample(range(1, 91), 90)
                        if user_count == MAX_USER:
                                cards = []
                                for i in range(user_count):
                                        card = random.sample(range(1,91), 15)
                                        cards.append(card)
                                session_info[self.session]['cards'] = cards
                                                        
                                response = 'NEW ' + str(cards.pop())
                                
                elif request[0:3] == 'NXT':
                        user_count = len(session_info[self.session]['users'])
                        session_info[self.session]['users'][self.csoc]['state'] = '1' #user is ready for next number
                        
                        while True:
                                ready_count = self.countReadyClients()
                                if ready_count == user_count:
                                        break
                        
                        if ready_count == user_count:
                                next_number = session_info[self.session]['random_numbers'].pop()
                                session_info[self.session]['past_numbers'] = []
                                session_info[self.session]['past_numbers'].append(next_number)
                                response = "NUM " + str(next_number)
                                
                                keys = session_info[self.session]['users'].keys()
                                for key in keys:
                                        session_info[self.session]['users'][key]['state'] = '0'  #user's next state is 0 for next number
                              
                                        
                elif request[0:3] == 'CNK': #session info holds 'cinko_rows' for cinko state for every user in the session
                        parameter = data[4:]
                        values = re.search(r"OrderedDict\((.*)\)", parameter).group(1)
                        card = OrderedDict(ast.literal_eval(values)) #string to orderedDict
                        cinko_list = self.checkCinko(card)
                        session_info[self.session]['users'][self.csoc]['cinko_rows'] = cinko_list
                        
                        if cinko_list:
                                response = "COK " + self.nickname + " " + ":".join(cinko_list)
                        else:
                                response = 'CER'
                                
                elif request[0:3] == 'TOM':
                        parameter = data[4:]
                        values = re.search(r"OrderedDict\((.*)\)", parameter).group(1)
                        card = OrderedDict(ast.literal_eval(values)) 
                        cinko_list = self.checkCinko(card)
                        session_info[self.session]['users'][self.csoc]['cinko_rows'] = cinko_list
                        if len(cinko_list) == 3:
                                response = "TOK " + self.nickname

                        else:
                                response = "TER"
                                
                elif request[0:3] == 'FIN':
                        #todo: remove session if every user displayed game over message
                               
                        response = 'END'

                else:
                        response = 'ERR'
                        
                print response
                if response[0:3] in ['NUM', 'COK', 'TOK']: 
                        broadcastResponse(self.session, response)
                else:
                        self.csoc.send(response)
                return 
		
        def getUsersofSession(self):
		client_list = session_info[self.session].keys()
		user_list = []
		for client in client_list:
			user_list.append(user_info[client]['nick'])
                return user_list

        def countReadyClients(self):
                clients = session_info[self.session]['users'].keys()
                count = 0
                for csoc in clients:
                        state = session_info[self.session]['users'][csoc]['state']
                        if state == '1':
                                count += 1
                return count
        
        def checkCinko(self, card):
            loop = 0
            first = 0
            second = 0
            third = 0
            cinkos = []
            for state in card.values():
                if state == '* ':
                    if loop >= 0 and loop <5:
                        first += 1
                    if loop >= 5 and loop <10:
                        second += 1
                    if loop >= 10 and loop <15:
                        third +=1
                loop += 1

            if first == 5:
                cinkos.append("1")
            if second == 5:
                cinkos.append("2")
            if third == 5:
                cinkos.append("3")
            return cinkos
                
		
	def run(self):
		while True: #for default client commands
                        data = self.csoc.recv(1024)
			print data
			self.incoming_parser(data) 
			

def broadcastResponse(session, response):
	clients = session_info[session]['users'].keys()
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

